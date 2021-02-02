import json
import os
import subprocess
from datetime import datetime

import git

# TODO: Change print to logging statements
from github_repo_loc_analyser.data_structure import PossibleRepo


class CodeAnalyzer:
    WORK_DIR = "./repos/"
    CLOCK_EXECUTABLE = "cloc"

    def __init__(self, repo: PossibleRepo, repo_branch="master"):
        self.repo = repo
        self.repo_branch = repo_branch

    def clone_repo(self):
        print('Cloning repository ' + self.repo.get_name() + '...')

        if not os.path.exists(self.WORK_DIR):
            os.makedirs(self.WORK_DIR)

        git.Git(self.WORK_DIR).clone(self.repo.get_commits_url())

    def process_repo(self):
        print('Begin processing repository ' + self.repo.get_name() + '...')
        if not os.path.exists(self.WORK_DIR + self.repo.get_name()):
            self.clone_repo()

        git_repo = git.Repo(self.WORK_DIR + self.repo.get_name())
        gcmd = git.cmd.Git(self.WORK_DIR)
        gcmd.pull()
        print('Checking out branch ' + self.repo_branch + " for repository " + self.repo.get_name() + '...')
        git_repo.git.checkout("-f", self.repo_branch)

        print('Obtaining cloc report for repository ' + self.repo.get_name() + '...')
        log_time = datetime.now().strftime("%Y%m%d%H%M%S")
        output_file = self.repo.get_name() + "-" + self.repo_branch + "-" + log_time + ".json"

        proc = subprocess.Popen(
            [self.CLOCK_EXECUTABLE, self.WORK_DIR + self.repo.get_name(), "--include-lang=" + self.repo.get_language(),
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

        return output


if __name__ == '__main__':
    # TODO: Remove this main section. it is for debugging purposes, only.
    test_repo_url = "https://github.com/dannyloweatx/checkmarx.git"
    test_repo = PossibleRepo("checkmarx", "Python", False, test_repo_url)
    analyzer = CodeAnalyzer(test_repo)
    dict = analyzer.process_repo()
    # pprint(dict)
