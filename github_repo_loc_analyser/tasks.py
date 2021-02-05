"""Module for the celery tasks."""

from json import dumps, loads

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


@app.task
def process_possible_repo(repo: PossibleRepo) -> Result:
    """Process the given possible repo."""
    slave = Slave(repo)
    return slave.run()
