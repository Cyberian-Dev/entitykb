from typing import List, Dict, Optional
from fastapi import APIRouter

from .instance import Instance
from .schemas import TextLabelsInput, SuggestInput
from entitykb import LabelSet

router = APIRouter()


@router.post("/add/", summary="Add entities to KB index.")
async def add(request) -> List[Dict]:
    pass


@router.post("/commit/", summary="Commit KB changes to disk.")
async def commit() -> Dict:
    kb = Instance.get()
    kb.commit()
    return kb.info()


@router.post("/find/", summary="Find entities from text.")
async def find(request: TextLabelsInput) -> List[Dict]:
    kb = Instance.get()
    label_set = LabelSet(labels=request.labels)
    results = kb.find(request.text, label_set)
    return [entity.dict() for entity in results]


@router.post("/find_one/", summary="Find entities from text.")
async def find_one(request: TextLabelsInput) -> Optional[List[Dict]]:
    kb = Instance.get()
    label_set = LabelSet(labels=request.labels)
    entity = kb.find_one(request.text, label_set)
    return entity.dict() if entity else None


@router.post("/info/", summary="Get configuration and meta data info.")
async def info() -> Dict:
    kb = Instance.get()
    return kb.info()


@router.post("/process/", summary="Parse text and return doc object.")
async def process(request: TextLabelsInput) -> Dict:
    kb = Instance.get()
    label_set = LabelSet(labels=request.labels)
    return kb.process(request.text, label_set=label_set).dict()


@router.post("/reload/", summary="Reload Knowledge Base from disk.")
async def reload() -> Dict:
    kb = Instance.get()
    kb.reload()
    return kb.info()


@router.post("/suggest/", summary="Find entities from text.")
async def suggest(request: SuggestInput) -> List[str]:
    kb = Instance.get()
    label_set = LabelSet(labels=request.labels)
    results = kb.suggest(
        term=request.term, label_set=label_set, limit=request.limit
    )
    return results
