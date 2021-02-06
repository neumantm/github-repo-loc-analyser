"""Module for querying the Github API."""
import logging
from random import randint
from typing import List, Optional
from time import sleep, time
from math import ceil

import requests

from . import CONFIG
from .data_structure import PossibleRepo
from .helper import sanitize_filename

logger: logging.Logger = logging.getLogger("gh_api")

API_SERVER = "https://api.github.com/"
API_ENDPOINT_REPOS = "search/repositories"

RATE_LIMIT_RETRIES = 3
REQUESTED_PAGE_SIZE = 100


class ApiQuerier:
    """Class for querying the github api."""

    def __init__(self):
        logger.debug("Init.")
        if "repo_filters" not in CONFIG:
            logger.error("Need the repo_filter config section.")
        repo_filters = CONFIG["repo_filters"]
        languages = repo_filters["languages"]
        self.languages: List[str] = languages.split(",")
        self.size: str = repo_filters["size"]
        self.stars: str = repo_filters["stars"]
        self.old_repo_created: str = repo_filters["old_repo_created"]
        self.old_repo_updated: str = repo_filters["old_repo_updated"]
        self.new_repo_created: str = repo_filters["new_repo_created"]
        self.new_repo_updated: str = repo_filters["new_repo_updated"]

        main = CONFIG["main"]

        self.num_repos_per_page: int = main.getint("num_repos_per_page")
        self.num_repo_pages: int = main.getint("num_repo_pages")
        self.old_repo_date: int = main.get("old_repo_date")
        self.new_repo_date: int = main.get("new_repo_date")

    def _perform_request_with_retry(self, request: requests.PreparedRequest) -> requests.Response:
        retries = 0
        while retries < RATE_LIMIT_RETRIES:
            logger.info("Performing request to {}. Try #{}".format(request.url.split('?')[0], retries))
            logger.debug("Full URL:{}".format(request.url))
            r = requests.Session().send(request)
            logger.debug("Status code: {}".format(r.status_code))
            if not (r.status_code == 403 and "rate limit exceeded" in r.text):
                return r
            current_time = ceil(time())
            time_for_rl_reset = int(r.headers['X-RateLimit-Reset'])
            to_sleep = time_for_rl_reset - current_time
            to_sleep = max(0, to_sleep)
            retries += 1
            logger.warn("Rate limit exeeded. Waiting {} seconds.".format(to_sleep))
            sleep(to_sleep)

    def _construct_get_repos_request(self, language: str, old_repo: bool) -> requests.Request:
        params = "q=language:" + language + "+"
        params += "size:" + self.size + "+"
        params += "stars:" + self.stars + "+"
        if old_repo:
            params += "created:" + self.old_repo_created + "+"
            params += "pushed:" + self.old_repo_updated
        else:
            params += "created:" + self.new_repo_created + "+"
            params += "pushed:" + self.new_repo_updated
        params += "&per_page=" + str(REQUESTED_PAGE_SIZE)
        url = API_SERVER + API_ENDPOINT_REPOS
        headers = {"Accept": "application/vnd.github.v3+json"}
        return requests.Request('GET', url, params=params, headers=headers)

    def _get_next_url(self, resp: requests.Response) -> Optional[str]:
        links = resp.headers["Link"].split(",")
        next_url = None
        for link in links:
            parts = link.split(";")
            if parts[1].strip() == 'rel="next"':
                next_url = parts[0].strip().strip("<").strip(">")
        return next_url

    def _get_repos(self, language: str, old_repo: bool, results_sanitzed_filenames: List[str]) -> List[PossibleRepo]:
        old_repo_string = "new"
        if old_repo:
            old_repo_string = "old"
        logger.info("Getting {} repos for {}.".format(old_repo_string, language))
        req = self._construct_get_repos_request(language, old_repo)

        result = []

        for page in range(self.num_repo_pages):
            logger.info("Getting page {}".format(page))
            resp = self._perform_request_with_retry(req.prepare())
            if not resp.ok:
                logger.error("Result not ok ({}): \n{}".format(resp.status_code, resp.text))

            if page < self.num_repo_pages - 1:
                url = self._get_next_url(resp)
                if url is None:
                    logger.error("Cannot get next page from headers:{}".format(resp.headers))
                req.url = url

            data = resp.json()
            used_indices = []
            for _ in range(self.num_repos_per_page):
                size = len(data["items"])
                last_i = size - 1
                index = -1
                sanitized_filename = ""
                datum = None
                tries = 0
                while index < 0 or index in used_indices or sanitized_filename in results_sanitzed_filenames:
                    tries += 1
                    if tries >= size * 2:
                        raise ValueError("Cannot find another usable entry in this result page.")
                    index = randint(0, last_i)
                    datum = data["items"][index]
                    name = datum["full_name"]
                    sanitized_filename = sanitize_filename(name)
                used_indices.append(index)
                results_sanitzed_filenames.append(sanitized_filename)
                logger.debug("Picked index: {}".format(index))
                remote_url = datum["clone_url"]
                commits_url = datum["commits_url"]
                commits_url = commits_url.split("{")[0]
                result.append(PossibleRepo(datum["full_name"], language, old_repo, remote_url, commits_url))

        return result

    def get_repos(self) -> List[PossibleRepo]:
        result = []
        results_sanitzed_filenames = [] # List to keep track of all the filenames we need as not to create a collision
        for language in self.languages:
            for old_repo in [False, True]:
                result += self._get_repos(language.strip(), old_repo, results_sanitzed_filenames)
        return result

    def get_commit(self, repo: PossibleRepo) -> str:
        """Get the hash of the commit to inspect for the given repo."""
        url = repo.get_commits_url()
        date = ""
        if repo.is_old_repo():
            date = self.old_repo_date
        else:
            date = self.new_repo_date
        params = {
            'until': date,  # Only get commits before our cut off date
            'per_page': 1  # We only want the last commit (list is sorted by order of commits) before the date
        }
        headers = {"Accept": "application/vnd.github.v3+json"}
        req = requests.Request('GET', url, params=params, headers=headers)
        logger.info("Getting commit hash for repo {}".format(repo.get_name()))
        resp = self._perform_request_with_retry(req.prepare())
        if not resp.ok:
            logger.error("Result not ok ({}): \n{}".format(resp.status_code, resp.text))
        data = resp.json()
        sha = data[0]["sha"]
        logger.debug("Commit: {}".format(sha))
        return sha
