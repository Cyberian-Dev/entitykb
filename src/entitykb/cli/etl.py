import csv
from typing import Iterator, List

from entitykb import Entity


def iterate_entities(
    in_file: str,
    dialect: str,
    mv_keys: List[str] = None,
    mv_sep="|",
    label="ENTITY",
    name=None,
    synonyms=None,
    key_format="{name}|{label}",
    ignore: list = None,
) -> Iterator[Entity]:

    reader = csv.DictReader(in_file, dialect=dialect)

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
