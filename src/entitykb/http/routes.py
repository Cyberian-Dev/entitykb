from dataclasses import asdict

from fastapi import APIRouter, Body

from entitykb import rpc
from . import schema

router = APIRouter()
rpc = rpc.RPCConnection()


@router.post("/parse", response_model=schema.Doc)
async def process(request: schema.ParseRequest = Body(...)) -> schema.Doc:
    """ Parse text and return document object. """
    async with rpc as client:
        data: dict = await client.call("parse", request.text, *request.labels)
        return data


@router.post("/entity")
async def save_entity(entity: schema.Entity = Body(...)):
    async with rpc as client:
        await client.call("save_entity", asdict(entity))


@router.post("/reset")
async def reset() -> bool:
    async with rpc as client:
        success: bool = await client.call("reset")
        return success


@router.post("/commit")
async def commit() -> int:
    async with rpc as client:
        commit_count: int = await client.call("commit")
        return commit_count


@router.post("/info")
async def info() -> int:
    async with rpc as client:
        data: dict = await client.call("info")
        return data
