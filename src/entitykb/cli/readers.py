import csv
import json

from entitykb import Entity, Envelope
from .cli import cli


@cli.register_reader("csv")
def csv_reader(file_obj):
    reader = csv.DictReader(file_obj, dialect="excel")
    for data in reader:
        entity = Entity.create(**data)
        yield entity


@cli.register_reader("tsv")
def tsv_reader(file_obj):
    reader = csv.DictReader(file_obj, dialect="excel-tab")
    for data in reader:
        entity = Entity.create(**data)
        yield entity


@cli.register_reader("jsonl")
def jsonl_reader(file_obj):
    for line in file_obj:
        envelope = Envelope(json.loads(line))
        yield envelope.payload
