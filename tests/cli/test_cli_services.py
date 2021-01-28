from pathlib import Path

from entitykb.cli import services


def test_flatten_dict():
    nested = dict(a=dict(b=1, c=2), d=(3, 4), e=dict(f=dict(g=5)))
    flat = services.flatten_dict(nested)
    assert {"a.b": 1, "a.c": 2, "d": "3\n4", "e.f.g": 5} == flat


def test_init_kb(root):
    assert isinstance(root, Path)
    assert root.exists()
    assert root.is_dir()
    assert set() == set(root.iterdir())

    assert services.init_kb(root, exist_ok=True)
    assert {
        "nodes",
        "config.json",
        "edges",
        "users",
    } == set(f.name for f in root.iterdir())

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
