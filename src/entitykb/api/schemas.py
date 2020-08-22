from typing import List
from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

    def dict(self, **kwargs):
        kwargs = {"exclude_defaults": True, **kwargs}
        return super(BaseModel, self).dict(**kwargs)


# API requests


class TextLabelsInput(BaseModel):
    text: str
    labels: List[str] = None


class SuggestInput(BaseModel):
    term: str
    labels: List[str] = None
    limit: int = 100


# schema versions of entitykb.model only used for API due to overhead
# of using Pydantic and it's validation engine


class DocToken(BaseModel):
    token: str
    offset: int


class Entity(BaseModel):
    name: str
    label: str = None
    synonyms: List[str] = None
    meta: dict = None


class DocEntity(BaseModel):
    text: str
    tokens: List[DocToken]
    entity: Entity


class Doc(BaseModel):
    text: str
    tokens: List[DocToken]
    entities: List[DocEntity]
