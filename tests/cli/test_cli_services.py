import os
from io import StringIO
from unittest.mock import MagicMock

from entitykb.cli import services, readers


def test_preview_mode():
    echo = MagicMock()
    preview = services.PreviewKB(echo=echo)

    file_obj = StringIO(data)
    it = readers.iterate_csv(file_obj)
    for entity in it:
        preview.save_node(entity)

    assert 3 == len(preview.dry_run)

    preview.commit()
    assert 3 == echo.call_count


def test_flatten_dict():
    nested = dict(a=dict(b=1, c=2), d=(3, 4), e=dict(f=dict(g=5)))
    flat = services.flatten_dict(nested)
    assert {"a.b": 1, "a.c": 2, "d": (3, 4), "e.f.g": 5} == flat


def test_init_kb(root):
    assert isinstance(root, str)
    assert os.path.exists(root)
    assert os.path.isdir(root)
    assert [] == os.listdir(root)

    assert services.init_kb(root, exist_ok=True)
    assert {"config.json", "index.db"} == set(os.listdir(root))

    assert services.init_kb(root, exist_ok=False) is False


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
