"""Module for the logic of the master node."""
import logging
from json import dump, load
from os import path, mkdir
from typing import List
from time import sleep

from celery.result import AsyncResult
from celery.exceptions import TimeoutError

from . import CONFIG
from .data_structure import PossibleRepo, Result, Repo
from .github_api_querier import ApiQuerier
from .helper import SerializableJsonDecoder, sanitize_filename
from .helper import atmoic_write_file, SerializableJsonEncoder
from .tasks import process_possible_repo

logger: logging.Logger = logging.getLogger("master")

REPOS_FILENAME = "repos.json"
RESULTS_DIRNAME = "results"


class Master:
    """Class containing the logic of the master node."""

    def __init__(self):
        """Init."""
        data_dir = CONFIG["main"]["data_dir"]
        self._repos_file = path.join(data_dir, REPOS_FILENAME)
        self._results_dir = path.join(data_dir, RESULTS_DIRNAME)
        self._min_tasks_in_queue = CONFIG["main"].getint("min_tasks_in_queue")
        self._max_tasks_in_queue = CONFIG["main"].getint("max_tasks_in_queue")
        if not path.exists(self._results_dir):
            mkdir(self._results_dir)
        self._waiting_for_results_for = []

    def create_repos_file(self):
        """Query the GH Api to create the repos file."""
        logger.info("Creating repos file.")
        api = ApiQuerier()
        possible_repos = api.get_repos()
        logger.debug("Atomic write repos file...")
        atmoic_write_file(self._repos_file, lambda f: dump(possible_repos, f, indent="  ", cls=SerializableJsonEncoder))

    def get_filepath_for_repo(self, repo: Repo):
        """Get the filepath for the data for the given repo."""
        filename = sanitize_filename(repo.get_name(), repo.get_language()) + ".json"
        return path.join(self._results_dir, filename)

    def start(self):
        """Start the master."""
        if not path.exists(self._repos_file):
            self.create_repos_file()
        logger.info("Loading repos file")
        with open(self._repos_file) as f:
            repos: List[PossibleRepo] = load(f, cls=SerializableJsonDecoder)

        for repo in repos:
            filepath = self.get_filepath_for_repo(repo)
            logger.debug("Looking at repo {}. Filename: {}".format(repo.get_name(), filepath))
            if path.exists(filepath):
                logger.debug("File exists")
                continue

            logger.info("Delegating task for repo {}".format(repo.get_name()))
            r = process_possible_repo.delay(repo)
            self._waiting_for_results_for.append(r)
            if len(self._waiting_for_results_for) > self._min_tasks_in_queue:
                oldest_result = self._waiting_for_results_for[0]
                try:
                    self.process_result(oldest_result)
                except TimeoutError:
                    pass
            index = 0
            while len(self._waiting_for_results_for) > self._max_tasks_in_queue:
                result_to_get = self._waiting_for_results_for[index]
                try:
                    self.process_result(result_to_get)
                except TimeoutError:
                    pass
                index = (index + 1) % len(self._waiting_for_results_for)

        for item in self._waiting_for_results_for:
            self.process_result(item)

    def process_result(self, result: AsyncResult):
        """Process the result of a process possible repo task."""
        analysis_result: Result = result.get(timeout=1)
        self._waiting_for_results_for.remove(result)
        if analysis_result is None:
            logger.warn("Got None result. Ignoring")
            return  # Error occurred. Don't save anything
        logger.debug("Got some result.")
        repo = analysis_result.get_repo()
        logger.info("Got result for {}".format(repo.get_name()))
        filepath = self.get_filepath_for_repo(repo)
        logger.debug("Atomically writing result for {}".format(repo.get_name()))
        atmoic_write_file(filepath, lambda f: dump(analysis_result, f, indent="  ", cls=SerializableJsonEncoder))
