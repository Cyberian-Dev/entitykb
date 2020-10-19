import collections
import csv
import enum
import os

import typer
from tabulate import tabulate

from entitykb import Config, KB, logger, Entity


class FileFormat(str, enum.Enum):
    csv = "csv"
    tsv = "tsv"

    @property
    def dialect(self):
        return {"csv": "excel", "tsv": "excel-tab"}.get(self.value)


def iterate_entities(file_obj, file_format, default_label=None, multi=None):
    reader = csv.DictReader(file_obj, dialect=file_format.dialect)
    mv_keys, mv_sep = multi if multi else ({"synonyms"}, "|")

    for record in reader:

        for mv_key in mv_keys:
            value = record.get(mv_key)
            if isinstance(value, str):
                value = value.strip()
                record[mv_key] = tuple(filter(None, value.split(mv_sep)))

        if default_label:
            record.setdefault("label", default_label)

        item = Entity.create(record)
        yield item


class PreviewKB(object):
    def __init__(self, echo=None, *_, **kwargs):
        self.dry_run = []
        self.length = kwargs.get("length", 10)
        self.echo = echo or typer.echo

    def save_node(self, entity):
        if len(self.dry_run) < self.length:
            d = entity.dict()
            d.pop("key", None)
            d.pop("attrs", None)
            self.dry_run.append(d)

    def commit(self):
        output = tabulate(
            self.dry_run,
            headers="keys",
            tablefmt="pretty",
            colalign=("left",) * 3,
        )
        self.echo(output)


def init_kb(root_dir, exist_ok=False) -> bool:
    success = False

    try:
        root_dir = Config.get_root_dir(root_dir)

        os.makedirs(root_dir, exist_ok=exist_ok)
        Config.create(root_dir=root_dir)

        kb = KB(root_dir=root_dir)
        kb.commit()
        success = True

    except FileExistsError as e:
        logger.error(e)

    return success


def flatten_dict(d, parent_key="", sep="."):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
