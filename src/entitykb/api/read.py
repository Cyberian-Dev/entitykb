from typing import Dict, Optional, List

from fastapi import APIRouter, Depends

from . import get_kb, KB, schemas, LabelSet

router = APIRouter()


@router.post("/info", summary="Get configuration and meta data info.")
async def info(kb: KB = Depends(get_kb)) -> Dict:
    return kb.info()


@router.post("/find", summary="Find entities from text.")
async def find(
    request: schemas.TextLabelsInput, kb: KB = Depends(get_kb)
) -> List[Dict]:
    label_set = LabelSet(labels=request.labels)
    results = kb.find(request.text, label_set)
    return [entity.dict() for entity in results]


@router.post("/find_one", summary="Find entities from text.")
async def find_one(
    request: schemas.TextLabelsInput, kb: KB = Depends(get_kb)
) -> Optional[List[Dict]]:
    label_set = LabelSet(labels=request.labels)
    entity = kb.find_one(request.text, label_set)
    return entity.dict() if entity else None


@router.post("/process", summary="Parse text and return doc object.")
async def process(
    request: schemas.TextLabelsInput, kb: KB = Depends(get_kb)
) -> Dict:
    label_set = LabelSet(labels=request.labels)
    return kb.process(request.text, label_set=label_set).dict()


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
