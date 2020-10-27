import tempfile
from typing import Union

import pytest

from entitykb.models import Node, Entity
from entitykb import KB


@pytest.fixture()
def root():
    return tempfile.mkdtemp()


@pytest.fixture()
def kb(root):
    return KB(root=root)


class Location(Node):
    def __init__(self, *, city: str, **kw):
        super().__init__(**kw)
        self.city = city

    def dict(self):
        return dict(city=self.city)

    @classmethod
    def convert(cls, value: Union[dict, "Location"]):
        if isinstance(value, dict):
            return cls(**value)
        else:
            return value


class Company(Entity):
    def __init__(self, *, headquarters: Location = None, **kwargs):
        super().__init__(**kwargs)
        self.headquarters = Location.convert(headquarters)

    def dict(self):
        data = super(Company, self).dict()
        hq_dict = self.headquarters.dict() if self.headquarters else None
        return {**data, "headquarters": hq_dict}


the_the = Entity(name="The The", label="BAND")


@pytest.fixture(scope="function")
def apple():
    return Company(
        name="Apple, Inc.",
        synonyms=("Apple", "AAPL"),
        headquarters=Location(city="Cupertino"),
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
