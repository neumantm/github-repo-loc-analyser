"""Module for the logic in the slave nodes."""
from .code_analyser import CodeAnalyzer
from .data_structure import PossibleRepo, Result, AnalysisRepo


class Slave:
    """Class containing the logic of the slave node."""

    def __init__(self, repo: PossibleRepo):
        """Init."""
        self._possible_repo = repo

    def run(self) -> Result:
        """Run the slave logic."""

        # TODO: Find commit we want and pass to code_analyzer
        repo_remote_url = ""  # TODO
        commit_hash = ""  # TODO
        repo = AnalysisRepo(self._possible_repo.get_name(), self._possible_repo.get_language(),
                            self._possible_repo.is_old_repo(), repo_remote_url, commit_hash)
        analyzer = CodeAnalyzer(repo)
        return analyzer.process_repo()
