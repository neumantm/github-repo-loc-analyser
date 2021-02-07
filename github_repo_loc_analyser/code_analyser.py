import json
import os
import subprocess
import shutil
import logging

import git

from . import CONFIG

from github_repo_loc_analyser.data_structure import AnalysisRepo, Result

logger: logging.Logger = logging.getLogger("codeana")

github_to_cloc_lookup_table = {
    "Java": "Java",
    "Python": "Python",
    "cpp": "C++",
    "Go": "Go",
    "Lua": "Lua",
    "Perl": "Perl",
    "PHP": "PHP",
    "Ruby": "Ruby",
    "JavaScript": "JavaScript",
    "Objective-C": "Objective-C"
}


class CodeAnalyzer:
    CLOCK_EXECUTABLE = "cloc"

    def __init__(self, repo: AnalysisRepo):
        self.repo = repo
        self.WORK_DIR = os.path.join(CONFIG["main"]["tmp_dir"], "repo/")

    def shallow_clone_repo(self):
        logger.info('Cloning repository ' + self.repo.get_name() + '...')

        if os.path.exists(self.WORK_DIR):
            shutil.rmtree(self.WORK_DIR)
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
        logger.info('Begin processing repository ' + self.repo.get_name() + '...')
        if not os.path.exists(self.WORK_DIR + self.repo.get_name()):
            self.shallow_clone_repo()

        logger.info('Obtaining cloc report for repository ' + self.repo.get_name() + '...')

        gh_lang = self.repo.get_language()
        if gh_lang not in github_to_cloc_lookup_table:
            raise ValueError("Unsupported language: {}".format(gh_lang))
        lang = github_to_cloc_lookup_table[gh_lang]

        proc = subprocess.Popen(
            [self.CLOCK_EXECUTABLE, self.WORK_DIR, "--include-lang=" + lang,
             "--json"],  # "--quiet"
            stdout=subprocess.PIPE)
        cloc_output = proc.stdout.read()
        if len(cloc_output) < 1:
            txt = "Cloc could not find any data for language {}".format(lang)
            logger.info(txt)
            return Result(self.repo, False, failure_reason=txt)
        try:
            output = json.loads(cloc_output)
        except json.decoder.JSONDecodeError as e:
            raise ValueError("Output cannot be parsed as json. Cloc output is: {}".format(cloc_output)) from e
        logger.debug("Got cloc output:{}".format(output))

        lang_result = output[lang]
        code_lines = lang_result["code"]
        if code_lines < CONFIG["main"].getint("minimum_code_lines"):
            txt = "To few code lines ({}) for language {}".format(code_lines, lang)
            logger.info(txt)
            return Result(self.repo, False, failure_reason=txt, analysis=lang_result)

        return Result(self.repo, True, analysis=lang_result)
