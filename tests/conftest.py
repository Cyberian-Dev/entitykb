import tempfile

import pytest

from entitykb import KB
from entitykb.models import Node, Entity


@pytest.fixture()
def root():
    return tempfile.mkdtemp()


@pytest.fixture()
def kb(root):
    return KB(root=root)


class Location(Node):
    city: str


class Company(Entity):
    headquarters: Location = None


the_the = Entity(name="The The", label="BAND")


@pytest.fixture(scope="function")
def apple():
    return Company(
        name="Apple, Inc.",
        synonyms=("Apple", "AAPL"),
        headquarters=Location(key=1, city="Cupertino"),
    )


@pytest.fixture(scope="function")
def apple_records():
    return Company(
        name="Apple Records",
        synonyms=("Apple",),
        headquarters=Location(key=2, city="Abbey Road"),
    )


@pytest.fixture(scope="function")
def google():
    return Company(name="Google, Inc.", label="COMPANY", synonyms=("Google",))


@pytest.fixture(scope="function")
def amazon():
    return Company(
        name="Amazon, Inc.",
        synonyms=("Amazon", "AMZN"),
        headquarters=Location(city="Seattle"),
    )


@pytest.fixture(scope="function")
def microsoft():
    return Company(
        name="Microsoft Corporation",
        synonyms=[
            "Microsoft Corp",
            "MSFT",
            "Microsoft",
            "The Microsoft Corporation",
            "The Microsoft Corp",
        ],
    )
