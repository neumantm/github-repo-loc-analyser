"""Module for the celery tasks."""
import logging
import logging.config
from os import path, _exit
from json import dumps, loads
from typing import Optional
from celery import Celery
from celery.worker import WorkController
from kombu.serialization import register

from . import CONFIG, setup, configure_logging
from . import base_celery_conf
from .data_structure import PossibleRepo, Result
from .helper import SerializableJsonDecoder, SerializableJsonEncoder
from .slave import Slave

setup()
app = Celery(config_source=base_celery_conf)
app.conf.update(CONFIG["celery"])
configure_logging()
register('grla_json',
         lambda o: dumps(o, cls=SerializableJsonEncoder),
         lambda o: loads(o, cls=SerializableJsonDecoder),
         content_type="application/x-grla-json")

app.conf.accept_content = ["grla_json"]
app.conf.task_serializer = "grla_json"
app.conf.result_serializer = "grla_json"

logger: logging.Logger = logging.getLogger("tasks")


@app.task
def process_possible_repo(repo: PossibleRepo) -> Optional[Result]:
    """Process the given possible repo."""
    try:
        slave = Slave(repo)
        result = slave.run()
        if result is None:
            logger.error("Slave returned None result.")
        return result
    except BaseException as e:
        logger.exception("Caught exception in task. Returning None: {}")
        if "debug_abort_on_error" in CONFIG["main"] and CONFIG["main"].getboolean("debug_abort_on_error"):
            logger.error("Will exit.")
            _exit(1)
        return None
