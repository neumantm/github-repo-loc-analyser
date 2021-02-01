#!/usr/bin/env python3
import argparse
import logging
import logging.config
import shutil
from os import environ, path, makedirs
from pprint import pprint

from . import CONFIG
from .github_api_querier import ApiQuerier


class EnvDefault(argparse.Action):
    """Argparse action to use the env as fallback."""

    def __init__(self, envvar, required=True, default=None, **kwargs):
        if not default and envvar:
            if envvar in environ:
                default = environ[envvar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required,
                                         **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


def run(config_file: str):
    """Run the program using the given config file."""
    config_file_abs = path.abspath(config_file)
    dir_path = path.dirname(config_file_abs)
    CONFIG.read(config_file_abs)
    if "main" not in CONFIG:
        print("Missing config main section.")
        exit(1)
    if "logging_conf" in CONFIG["main"]:
        logging_config_path = path.join(dir_path, CONFIG["main"]["logging_conf"])
        logging.config.fileConfig(logging_config_path, disable_existing_loggers=False)
    logger = logging.getLogger("main")
    logger.info("Master log level: {}".format(logging.getLevelName(logging.root.level)))

    if "data_dir" not in CONFIG["main"]:
        logger.error("Need the data_dir configured in the main section of the config file.")
        exit(1)

    shutil.rmtree(CONFIG["main"]["data_dir"], ignore_errors=True)
    makedirs(CONFIG["main"]["data_dir"])

    api = ApiQuerier()
    pprint(str(api.get_repos()))


def main():
    """Run the script."""
    parser = argparse.ArgumentParser(
        description='Analyse a random set of repos for their lines of code and lines of comments')
    parser.add_argument('--config', '-c', metavar='file', action=EnvDefault, envvar='GRLA_CONFIG', required=False,
                        default="./grla.conf",
                        help='The config file to use. Defaults to "./grla.conf". Can also be specified via the environment variable GRLA_CONFIG')

    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
