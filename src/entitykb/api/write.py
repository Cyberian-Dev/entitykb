from typing import Dict, List

from fastapi import APIRouter, Depends

from . import get_kb, KB

router = APIRouter()


@router.post("/add", summary="Add entities to KB index.")
async def add(request) -> List[Dict]:
    pass


@router.post("/commit", summary="Commit KB changes to disk.")
async def commit(kb: KB = Depends(get_kb)) -> Dict:
    kb.commit()
    return kb.info()
