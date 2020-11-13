import csv
from io import FileIO

from entitykb import Entity, environ
from .commands import cli


@cli.register_format("csv")
def iterate_csv(file_obj: FileIO):
    reader = csv.DictReader(file_obj, dialect="excel")
    for data in reader:
        synonyms = data.pop("synonyms", "")
        if synonyms:
            data["synonyms"] = synonyms.split(environ.mv_split)
        entity = Entity.construct(data)
        yield entity
