"""The main github repo loc analyser module"""
import configparser
import logging
import logging.config
import shutil
from os import environ, path, makedirs

CONFIG: configparser.ConfigParser = configparser.ConfigParser()
_is_set_up = False
_logging_config_path = None

def configure_logging():
    global _logging_config_path
    if _logging_config_path is not None:
        logging.config.fileConfig(_logging_config_path, disable_existing_loggers=False)

def setup():
    """Setup config file and logging and so on."""
    global _is_set_up
    global _logging_config_path
    if _is_set_up:
        return
    _is_set_up = True
    if "GRLA_CONFIG" in environ:
        config_file = environ["GRLA_CONFIG"]
    else:
        config_file = "./grla.conf"
    config_file_abs = path.abspath(config_file)
    dir_path = path.dirname(config_file_abs)
    CONFIG.read(config_file_abs)
    if "main" not in CONFIG:
        print("Missing config main section.")
        exit(1)
    if "logging_conf" in CONFIG["main"]:
        _logging_config_path = path.join(dir_path, CONFIG["main"]["logging_conf"])
        configure_logging()

    logger = logging.getLogger("main")
    logger.info("Master log level: {}".format(logging.getLevelName(logging.root.level)))

    if "celery" not in CONFIG:
        logger.error("Need the celery section of the config file.")
        exit(1)

    if "data_dir" not in CONFIG["main"]:
        logger.error("Need the data_dir configured in the main section of the config file.")
        exit(1)

    data_dir = CONFIG["main"]["data_dir"]

    if "debug_remove_data" in CONFIG["main"] and CONFIG["main"].getboolean("debug_remove_data"):
        shutil.rmtree(data_dir, ignore_errors=True)

    if not path.isdir(data_dir):
        makedirs(data_dir)

    if "tmp_dir" not in CONFIG["main"]:
        logger.error("Need the tmp_dir configured in the main section of the config file.")
        exit(1)

    tmp_dir = CONFIG["main"]["tmp_dir"]

    shutil.rmtree(tmp_dir, ignore_errors=True)
    makedirs(tmp_dir)
