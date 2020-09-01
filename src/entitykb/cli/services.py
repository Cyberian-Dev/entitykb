import csv
import enum
import os
from typing import Iterator, List

import typer
from tabulate import tabulate

from entitykb import Config, KB, logger
from entitykb.model import Entity


class FileFormat(str, enum.Enum):
    csv = "csv"
    tsv = "tsv"

    @property
    def dialect(self):
        return {"csv": "excel", "tsv": "excel-tab"}.get(str(self))


def iterate_entities(
    in_file: str,
    format: FileFormat,
    mv_keys: List[str] = None,
    mv_sep="|",
    label="ENTITY",
    name=None,
    synonyms=None,
    key_format="{name}|{label}",
    ignore: list = None,
) -> Iterator[Entity]:

    in_file = open(in_file)
    reader = csv.DictReader(in_file, dialect=format.dialect)

    # defaults
    mv_keys = set(mv_keys or [])
    mv_keys.add("synonyms")
    mv_sep = mv_sep or "|"

    # iterate records
    seen = set()
    for record in reader:
        record.setdefault("name", "No 'name'")
        record.setdefault("label", label)

        if name:
            record["name"] = record.pop(name, f"No '{name}'")

        if synonyms and synonyms in record:
            record["synonyms"] = record.pop(synonyms)

        item = Entity.from_dict(
            record=record,
            mv_keys=mv_keys,
            mv_sep=mv_sep,
            key_format=key_format,
            ignore=ignore,
        )

        if item.key not in seen:
            yield item
            seen.add(item.key)


class PreviewKB(object):
    def __init__(self, *_, **kwargs):
        self.dry_run = []
        self.length = kwargs.get("length", 10)

    def save_entity(self, entity):
        if len(self.dry_run) < self.length:
            d = entity.dict()
            d.pop("key", None)
            d.pop("meta", None)
            self.dry_run.append(d)

    def commit(self):
        output = tabulate(
            self.dry_run,
            headers="keys",
            tablefmt="pretty",
            colalign=("left",) * 3,
        )
        typer.echo(output)


def init_kb(root_dir) -> bool:
    success = False

    try:
        root_dir = Config.get_root_dir(root_dir)

        os.makedirs(root_dir)
        Config.create(root_dir=root_dir)

        kb = KB(root_dir=root_dir)
        kb.commit()
        success = True

    except FileExistsError as e:
        logger.error(e)

    return success
