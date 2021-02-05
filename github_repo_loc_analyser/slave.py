"""Module for the logic in the slave nodes."""

from .data_structure import PossibleRepo, Result


class Slave:
    """Class containing the logic of the slave node."""

    def __init__(self, repo: PossibleRepo):
        """Init."""
        self._possible_repo = repo

    def run(self) -> Result:
        """Run the slave logic."""
        # TODO: Find commit we want and pass to code_analyzer
        return Result(self._possible_repo)
