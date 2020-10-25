import csv
from io import FileIO

from entitykb import Entity, environ
from .commands import cli


@cli.register_format("csv")
def iterate_csv(file_obj: FileIO):
    reader = csv.DictReader(file_obj, dialect="excel")
    for data in reader:
        synonyms = data.get("synonyms")
        if isinstance(synonyms, str):
            data["synonyms"] = synonyms.split(environ.mv_split)
        entity = Entity.create(data)
        yield entity
