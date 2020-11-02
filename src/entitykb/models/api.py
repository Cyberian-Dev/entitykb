from typing import List

from pydantic import BaseModel


class SuggestRequest(BaseModel):
    term: str


class ParseRequest(BaseModel):
    text: str
    pipeline: str = "default"
    labels: List[str] = []
