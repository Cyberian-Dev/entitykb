from typing import List

from pydantic import BaseModel


class SuggestRequest(BaseModel):
    term: str


class ParseRequest(BaseModel):
    text: str
    labels: List[str] = []
