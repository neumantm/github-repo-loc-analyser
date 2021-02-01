import os
import subprocess
from datetime import datetime

import git

from github_repo_loc_analyser.github_api_querier import PossibleRepo


# TODO: Change print to logging statements
class Analyzer:
    WORKDIR = "./"
    CLOCK_EXECUTABLE = "cloc"

    def __init__(self, repo: PossibleRepo, repo_branch="master"):
        self.repo = repo
        self.repo_branch = repo_branch

    def clone_repo(self):
        print('Cloning repository ' + self.repo.get_name() + '...')
        git.Git(self.WORKDIR).clone(self.repo.get_commits_url())

    def process_repo(self):
        repo_name = self.repo.get_name()
        print('Begin processing repository ' + repo_name + '...')
        if not os.path.exists(self.WORKDIR + repo_name):
            self.clone_repo()

        gitrepo = git.Repo(repo_name)
        gcmd = git.cmd.Git(repo_name)
        gcmd.pull()
        print('Checking out branch ' + self.repo_branch + " for repository " + repo_name + '...')
        gitrepo.git.checkout("-f", self.repo_branch)

        print('Obtaining cloc report for repository ' + repo_name + '...')
        log_time = datetime.now().strftime("%Y%m%d%H%M%S")
        output_file = repo_name + "-" + self.repo_branch + "-" + log_time + ".json"

        proc = subprocess.Popen(
            [self.CLOCK_EXECUTABLE, self.WORKDIR + repo_name, "--json", "--out", output_file, ],  # "--quiet"
            stdout=subprocess.PIPE)
        proc.stdout.read()


if __name__ == '__main__':
    test_repo_url = "https://github.com/dannyloweatx/checkmarx.git"
    repo = PossibleRepo("checkmarx", "java", test_repo_url)
    analyzer = Analyzer(repo)
    analyzer.process_repo()
