"""Module for querying the Github API."""
import logging
from random import randint
from typing import List

import requests

from . import CONFIG

logger: logging.Logger = logging.getLogger("gh_api")

API_SERVER = "https://api.github.com/"
API_ENDPOINT_REPOS = "search/repositories"


class PossibleRepo:
    def __init__(self, name, language, commits_url):
        self._name = name
        self._language = language
        self._commits_url = commits_url

    def get_name(self):
        return self._name

    def get_language(self):
        return self._language

    def get_commits_url(self):
        return self._commits_url


class ApiQuerier:
    """ Class for querying the github api. """

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

    def _build_query(self, language: str, old_repo: bool) -> str:
        result = "q=language:" + language + "+"
        result += "size:" + self.size + "+"
        result += "stars:" + self.stars + "+"
        if old_repo:
            result += "created:" + self.old_repo_created + "+"
            result += "pushed:" + self.old_repo_updated
        else:
            result += "created:" + self.new_repo_created + "+"
            result += "pushed:" + self.new_repo_updated
        return result

    def _get_repos(self, language: str, old_repo: bool) -> List[PossibleRepo]:
        old_repo_string = "new"
        if old_repo:
            old_repo_string = "old"
        logger.info("Getting {} repos for {}.".format(old_repo_string, language))
        r = requests.get(API_SERVER + API_ENDPOINT_REPOS,
                         params=self._build_query(language, old_repo),
                         headers={"Accept": "application/vnd.github.v3+json"})
        logger.debug("Status code: {}".format(r.status_code))
        if not r.ok:
            logger.error("Result not ok: \n{}".format(r.text))
            if r.status_code == 403 and "rate limit exceeded" in r.text:
                logger.warn("Rate limit exeeded")
        data = r.json()
        used_indices = []
        result = []
        for _ in range(self.num_repos_per_page):
            index = randint(0, 29)
            while index in used_indices:
                index = randint(0, 29)
            used_indices.append(index)
            logger.debug("Picked index: {}".format(index))
            datum = data["items"][index]
            commits_url = datum["commits_url"]
            commits_url = commits_url.split("{")[0]
            result.append(PossibleRepo(datum["full_name"], language, commits_url))

        return result

    def get_repos(self) -> List[PossibleRepo]:
        result = []
        for language in self.languages:
            for old_repo in [False, True]:
                result += self._get_repos(language.strip(), old_repo)
        return result
