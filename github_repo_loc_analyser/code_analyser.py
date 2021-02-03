import json
import os
import subprocess
from pprint import pprint

import git

# TODO: Change print to logging statements
from github_repo_loc_analyser.data_structure import AnalysisRepo, Result


class CodeAnalyzer:
    WORK_DIR = "./repo/"
    CLOCK_EXECUTABLE = "cloc"

    def __init__(self, repo: AnalysisRepo):
        self.repo = repo

    def shallow_clone_repo(self):
        print('Cloning repository ' + self.repo.get_name() + '...')

        if not os.path.exists(self.WORK_DIR):
            os.makedirs(self.WORK_DIR)

        git_repo = git.Repo.init(self.WORK_DIR, mkdir=True)
        if not git_repo.remotes:
            # add the remote if not already done in a previous run
            origin = git_repo.create_remote("origin", self.repo.get_remote_url())
            git_repo.remotes.append(origin)
        else:
            # origin already added
            origin = git_repo.remotes.origin
        assert origin.exists()
        assert git_repo.remotes.origin == git_repo.remotes['origin']
        git_repo.git.fetch("--depth", "1", "origin", self.repo.get_commit())

        git_repo.git.checkout("FETCH_HEAD")

    def process_repo(self) -> Result:
        print('Begin processing repository ' + self.repo.get_name() + '...')
        if not os.path.exists(self.WORK_DIR + self.repo.get_name()):
            self.shallow_clone_repo()

        print('Obtaining cloc report for repository ' + self.repo.get_name() + '...')

        proc = subprocess.Popen(
            [self.CLOCK_EXECUTABLE, self.WORK_DIR, "--include-lang=" + self.repo.get_language(),
             "--json"],  # "--quiet"
            stdout=subprocess.PIPE)
        cloc_output = proc.stdout.read()
        try:
            output = json.loads(cloc_output)
        except json.decoder.JSONDecodeError:
            raise ValueError(
                "Output cannot be parsed as json. "
                "Maybe \"" + self.repo.get_language() + "\" is not a valid language identifier. Cloc output is: "
                + str(cloc_output))

        return self._generate_output(output)

    def _generate_output(self, cloc_output):
        cloc_output = cloc_output[self.repo.get_language()]
        return Result(self.repo, cloc_output)


if __name__ == '__main__':
    # TODO: Remove this main section. it is for debugging purposes, only.
    test_repo_url = "https://github.com/neumantm/github-repo-loc-analyser.git"
    test_repo = AnalysisRepo("TestRepo", "Python", False, test_repo_url, "4e6dbcfe5e669bce3f80d86edadea8b1da5fdd28")
    analyzer = CodeAnalyzer(test_repo)
    analysis = analyzer.process_repo()
    pprint(analysis.get_analysis())
