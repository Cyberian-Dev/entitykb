from typing import Union

import pytest

from entitykb import BaseModel, Entity


class Location(BaseModel):
    def __init__(self, *, city: str):
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
        label="COMPANY",
        synonyms=("Apple", "AAPL"),
        meta=dict(top_product="iPhone"),
        headquarters=Location(city="Cupertino"),
    )


@pytest.fixture(scope="function")
def google():
    return Company(name="Google, Inc.", label="COMPANY", synonyms=("Google",))


@pytest.fixture(scope="function")
def amazon():
    return Company(
        name="Amazon, Inc.",
        label="COMPANY",
        synonyms=("Amazon", "AMZN"),
        meta=dict(top_product="Prime"),
        headquarters=Location(city="Seattle"),
    )


@pytest.fixture(scope="function")
def microsoft():
    return Company(
        name="Microsoft Corporation",
        label="COMPANY",
        synonyms=[
            "Microsoft Corp",
            "MSFT",
            "Microsoft",
            "The Microsoft Corporation",
            "The Microsoft Corp",
        ],
    )
