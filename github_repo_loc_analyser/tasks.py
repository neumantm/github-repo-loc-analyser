"""Module for the celery tasks."""
import logging
from json import dumps, loads
from typing import Optional
from celery import Celery
from kombu.serialization import register

from . import CONFIG, setup
from .data_structure import PossibleRepo, Result
from .helper import SerializableJsonDecoder, SerializableJsonEncoder
from .slave import Slave

setup()
app = Celery()
app.conf.update(CONFIG["celery"])
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
    except BaseException:
        logger.exception("Caught exception in task. Returning None")
        return None
