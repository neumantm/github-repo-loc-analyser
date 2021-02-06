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

    def __init__(self, name: str, language: str, old_repo: bool, remote_url: str):
        """Init."""
        super().__init__()
        self._name = name
        self._language = language
        self._old_repo = old_repo
        self._remote_url = remote_url

    def get_name(self) -> str:
        """Return the full name of the repo."""
        return self._name

    def get_language(self) -> str:
        """Return the lnagauge for which this repo was chosen."""
        return self._language

    def is_old_repo(self) -> bool:
        """Return whether this repo was chosen as an old repo (a repo in the older of the two timeperiods)."""
        return self._old_repo

    def get_remote_url(self) -> str:
        """Return the remote url (clone url) of the repo."""
        return self._remote_url

    def serialize(self) -> Dict:
        """See overridden."""
        data = super().serialize()
        data["name"] = self._name
        data["language"] = self._language
        data["old_repo"] = self._old_repo
        data["remote_url"] = self._remote_url
        return data

    @classmethod
    def deserialize(cls, data: Dict):
        """Return a new object from the given data."""
        return Repo(data["name"], data["language"], data["old_repo"], data["remote_url"])


class PossibleRepo(Repo):
    """The representation of a repo which might be used."""

    def __init__(self, name: str, language: str, old_repo: bool, remote_url: str, commits_url: str):
        """Init."""
        super().__init__(name, language, old_repo, remote_url)
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
        return PossibleRepo(data["name"], data["language"], data["old_repo"], data["remote_url"], data["commits_url"])


class AnalysisRepo(Repo):
    def __init__(self, name: str, language: str, old_repo: bool, remote_url: str, commit: str):
        """Init"""
        super().__init__(name, language, old_repo, remote_url)
        self._commit = commit

    def get_commit(self) -> str:
        return self._commit

    def serialize(self) -> Dict:
        """See overridden."""
        data = super().serialize()
        data["commit"] = self._commit
        return data

    @classmethod
    def deserialize(cls, data: Dict):
        """Return a new object from the given data."""
        return AnalysisRepo(data["name"], data["language"], data["old_repo"], data["remote_url"], data["commit"])


class Result(Serializable):
    """The result of the repo analysis."""

    def __init__(self, repo, sucess=True, analysis=None, failure_reason=None):
        """Init."""
        super().__init__()
        self._repo = repo
        self._success = sucess
        self._analysis = analysis
        self._failure_reason = failure_reason

    def get_repo(self) -> Repo:
        """Return the repo this result is for."""
        return self._repo

    def is_success(self) -> bool:
        return self._success

    def get_analysis(self) -> dict:
        return self._analysis

    def failure_reason(self) -> str:
        return self._failure_reason

    def serialize(self) -> Dict:
        """See overridden."""
        data = super().serialize()
        data["repo"] = self._repo
        data["success"] = self._success
        data["analysis"] = self._analysis
        data["failure_reason"] = self._failure_reason
        return data

    @classmethod
    def deserialize(cls, data: Dict):
        """Return a new object from the given data."""
        return Result(data["repo"], data["success"], data["analysis"], data["failure_reason"])
