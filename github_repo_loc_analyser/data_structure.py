"""Module containing the data structure classes used by this project."""

from typing import Dict


class Serializable:
    """Class which can be serialized."""

    def serialize(self) -> Dict:
        """Return the data representing this class as a dict."""
        return {"_class": type(self).__name__}

    @classmethod
    def deserialize(cls, data: Dict):
        """Return a new object from the given data."""
        return Serializable()


class Repo(Serializable):
    """The basic representation of a repository."""

    def __init__(self, name: str, language: str, old_repo: bool):
        """Init."""
        super().__init__()
        self._name = name
        self._language = language
        self._old_repo = old_repo

    def get_name(self) -> str:
        """Return the full name of the repo."""
        return self._name

    def get_language(self) -> str:
        """Return the lnagauge for which this repo was chosen."""
        return self._language

    def is_old_repo(self) -> bool:
        """Return whether this repo was chosen as an old repo (a repo in the older of the two timeperiods)."""
        return self._old_repo

    def serialize(self) -> Dict:
        """See overridden."""
        data = super().serialize()
        data["name"] = self._name
        data["language"] = self._language
        data["old_repo"] = self._old_repo
        return data

    @classmethod
    def deserialize(cls, data: Dict):
        """Return a new object from the given data."""
        return Repo(data["name"], data["language"], data["old_repo"])


class PossibleRepo(Repo):
    """The representation of a repo which might be used."""

    def __init__(self, name: str, language: str, old_repo: bool, commits_url: str):
        """Init."""
        super().__init__(name, language, old_repo)
        self._commits_url = commits_url

    def get_commits_url(self) -> str:
        """Return the url of the api endpoint for getting the repo's commits."""
        return self._commits_url

    def serialize(self) -> Dict:
        """See overridden."""
        data = super().serialize()
        data["commits_url"] = self._commits_url
        return data

    @classmethod
    def deserialize(cls, data: Dict):
        """Return a new object from the given data."""
        return PossibleRepo(data["name"], data["language"], data["old_repo"], data["commits_url"])


class AnalysisRepo(Repo):
    def __init__(self, name: str, language: str, old_repo: bool, remote_url: str, commit: str):
        """Init"""
        super().__init__(name, language, old_repo)
        self._remote_url = remote_url
        self._commit = commit

    def get_remote_url(self) -> str:
        return self._remote_url

    def get_commit(self) -> str:
        return self._commit

    def serialize(self) -> Dict:
        """See overridden."""
        data = super().serialize()
        data["remote_url"] = self._remote_url
        data["commit"] = self._commit
        return data

    @classmethod
    def deserialize(cls, data: Dict):
        """Return a new object from the given data."""
        return AnalysisRepo(data["name"], data["language"], data["old_repo"], data["remote_url"], data["commit"])


class Result(Serializable):
    """The result of the repo analysis."""

    def __init__(self, repo, analysis):
        """Init."""
        super().__init__()
        self._repo = repo
        self._analysis = analysis

    def get_repo(self) -> Repo:
        """Return the repo this result is for."""
        return self._repo

    def get_analysis(self) -> dict:
        return self._analysis

    def serialize(self) -> Dict:
        """See overridden."""
        data = super().serialize()
        data["repo"] = self._repo
        data["analysis"] = self._analysis
        return data

    @classmethod
    def deserialize(cls, data: Dict):
        """Return a new object from the given data."""
        return Result(data["repo"], data["analysis"])
