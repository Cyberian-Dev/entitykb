from typing import List
from pydantic import BaseModel


class TextLabelsInput(BaseModel):
    text: str
    labels: List[str] = None


class SuggestInput(BaseModel):
    term: str
    labels: List[str] = None
    limit: int = 100
