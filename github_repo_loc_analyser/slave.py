"""Module for the logic in the slave nodes."""
from .code_analyser import CodeAnalyzer
from .data_structure import PossibleRepo, Result, AnalysisRepo
from .github_api_querier import ApiQuerier


class Slave:
    """Class containing the logic of the slave node."""

    def __init__(self, repo: PossibleRepo):
        """Init."""
        self._possible_repo = repo

    def run(self) -> Result:
        """Run the slave logic."""
        aq = ApiQuerier()
        commit_hash = aq.get_commit(self._possible_repo)
        repo = AnalysisRepo(self._possible_repo.get_name(), self._possible_repo.get_language(),
                            self._possible_repo.is_old_repo(), self._possible_repo.get_remote_url(), commit_hash)
        analyzer = CodeAnalyzer(repo)
        return analyzer.process_repo()
