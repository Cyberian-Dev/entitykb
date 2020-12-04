import csv
import json

from io import FileIO

from entitykb import Entity, environ, Node, Edge
from .commands import cli


@cli.register_format("csv")
def iterate_csv(file_obj: FileIO):
    reader = csv.DictReader(file_obj, dialect="excel")
    for data in reader:
        synonyms = data.pop("synonyms", "")
        if synonyms:
            data["synonyms"] = synonyms.split(environ.mv_split)
        entity = Entity.create(**data)
        yield entity


@cli.register_format("jsonl")
def iterate_jsonl(file_obj: FileIO):
    for line in file_obj:
        envelope = json.loads(line)
        kind, payload = envelope["kind"], envelope["payload"]
        if kind == "node":
            yield Node.create(**payload)

        elif kind == "edge":
            yield Edge.create(**payload)
