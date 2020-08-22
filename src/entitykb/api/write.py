from typing import Dict

from fastapi import APIRouter, Depends

from entitykb import Entity, KB
from . import get_kb, schemas

router = APIRouter()


@router.post("/add", summary="Add entities to KB index.")
async def add(
    request: schemas.Entity, kb: KB = Depends(get_kb)
) -> schemas.Entity:

    entity = Entity.from_dict(request.dict())
    kb.add(entity)
    response = schemas.Entity.from_orm(entity)
    return response


@router.post("/commit", summary="Commit KB changes to disk.")
async def commit(kb: KB = Depends(get_kb)) -> Dict:
    kb.commit()
    return kb.info()


@router.post("/reset", summary="Reset KB, removing all entities, terms, etc.")
async def reset(kb: KB = Depends(get_kb)) -> Dict:
    kb.reset()
    return kb.info()
