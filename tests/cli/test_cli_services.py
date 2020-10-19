import os
from io import StringIO
from unittest.mock import MagicMock

from entitykb.cli import services


def test_file_format_dialect():
    assert services.FileFormat.csv.dialect == "excel"
    assert services.FileFormat.tsv.dialect == "excel-tab"


def test_iterate_entities():
    file_obj = StringIO(data)
    it = services.iterate_entities(
        file_obj, services.FileFormat.csv, default_label="MISSING"
    )
    entities = list(it)
    assert 3 == len(entities)
    assert entities[0].name == "New York City"
    assert entities[0].synonyms == ("NYC", "New York (NY)")
    assert entities[0].label == "CITY"


def test_preview_mode():
    echo = MagicMock()
    preview = services.PreviewKB(echo=echo)

    file_obj = StringIO(data)
    it = services.iterate_entities(file_obj, services.FileFormat.csv)
    for entity in it:
        preview.save_node(entity)

    assert 3 == len(preview.dry_run)

    preview.commit()
    echo.assert_called_once_with(output)


def test_flatten_dict():
    nested = dict(a=dict(b=1, c=2), d=(3, 4), e=dict(f=dict(g=5)))
    flat = services.flatten_dict(nested)
    assert {"a.b": 1, "a.c": 2, "d": (3, 4), "e.f.g": 5} == flat


def test_init_kb(root_dir):
    assert isinstance(root_dir, str)
    assert os.path.exists(root_dir)
    assert os.path.isdir(root_dir)
    assert [] == os.listdir(root_dir)

    assert services.init_kb(root_dir, exist_ok=True)
    assert {"config.json", "index.db"} == set(os.listdir(root_dir))

    assert services.init_kb(root_dir, exist_ok=False) is False


data = """name,synonyms,label
New York City,NYC|New York (NY),CITY
New York,NY,STATE
United States,USA|US,COUNTRY"""

output = """+---------+---------------+--------------------------+
| label   | name          | synonyms                 |
+---------+---------------+--------------------------+
| CITY    | New York City | ('NYC', 'New York (NY)') |
| STATE   | New York      | ('NY',)                  |
| COUNTRY | United States | ('USA', 'US')            |
+---------+---------------+--------------------------+"""
