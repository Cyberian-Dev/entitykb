import json
from typing import Union

from pydantic.json import pydantic_encoder

from entitykb import Envelope, Node, Edge
from .cli import cli


@cli.register_writer("jsonl")
def jsonl_writer(file_obj, item: Union[Node, Edge]):
    envelope = Envelope(item)
    data = json.dumps(envelope, default=pydantic_encoder)
    file_obj.write(f"{data}\n")
