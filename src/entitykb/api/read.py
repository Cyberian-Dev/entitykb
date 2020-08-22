import threading
from typing import Dict, Optional, List

from fastapi import APIRouter, Depends

from entitykb import KB, LabelSet
from . import get_kb, schemas

router = APIRouter()


@router.get(
    "/info",
    summary="Get configuration and meta data info.",
    response_model=dict,
)
async def info(kb: KB = Depends(get_kb)) -> dict:
    return {**kb.info(), "thread_id": threading.get_ident()}


@router.post(
    "/find",
    summary="Find entities from text.",
    response_model=List[schemas.Entity],
)
async def find(
    request: schemas.TextLabelsInput, kb: KB = Depends(get_kb)
) -> List[schemas.Entity]:
    label_set = LabelSet(labels=request.labels)
    results = kb.find(request.text, label_set)
    return [schemas.Entity.from_orm(entity) for entity in results]


@router.post(
    "/find_one",
    summary="Return first found entity in text.",
    response_model=schemas.Entity,
)
async def find_one(
    request: schemas.TextLabelsInput, kb: KB = Depends(get_kb)
) -> Optional[List[Dict]]:
    label_set = LabelSet(labels=request.labels)
    entity = kb.find_one(request.text, label_set)
    return schemas.Entity.from_orm(entity) if entity else None


@router.post(
    "/process",
    summary="Parse text and return doc object.",
    response_model=schemas.Doc,
)
async def process(
    request: schemas.TextLabelsInput, kb: KB = Depends(get_kb)
) -> schemas.Doc:
    label_set = LabelSet(labels=request.labels)
    doc = kb.process(request.text, label_set=label_set)
    return schemas.Doc.from_orm(doc)


@router.post("/suggest", summary="Find entities from text.")
async def suggest(
    request: schemas.SuggestInput, kb: KB = Depends(get_kb)
) -> List[str]:
    label_set = LabelSet(labels=request.labels)
    results = kb.suggest(
        term=request.term, label_set=label_set, limit=request.limit
    )
    return results


@router.post("/reload", summary="Reload Knowledge Base from disk.")
async def reload(kb: KB = Depends(get_kb)) -> Dict:
    kb.load()
    return kb.info()
