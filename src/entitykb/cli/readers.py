import csv
from io import FileIO
from json import loads

from entitykb import Entity, environ, Node, Edge, Registry
from .commands import cli


@cli.register_format("csv")
def iterate_csv(file_obj: FileIO):
    registry = Registry.instance()
    reader = csv.DictReader(file_obj, dialect="excel")
    for data in reader:
        synonyms = data.pop("synonyms", "")
        if synonyms:
            data["synonyms"] = synonyms.split(environ.mv_split)
        entity = registry.create(Entity, data)
        yield entity


@cli.register_format("jsonl")
def iterate_jsonl(file_obj: FileIO):
    registry = Registry.instance()
    for line in file_obj:
        envelope = loads(line)
        kind, payload = envelope["kind"], envelope["payload"]
        if kind == "node":
            node = registry.create(Node, payload)
            yield node

        elif kind == "edge":
            edge = registry.create(Edge, payload)
            yield edge
