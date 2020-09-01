import os
from dataclasses import asdict

import uvicorn
from fastapi import FastAPI, APIRouter, staticfiles, Body
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import UJSONResponse

from entitykb import rpc, logger
from . import schema

app = FastAPI(
    title="EntityKB HTTP API",
    description="EntityKB HTTP API",
    default_response_class=UJSONResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        success: bool = await client.call("resent")
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


app.include_router(router)

# mount Admin UI
admin = os.path.join(os.path.dirname(__file__), "admin/public")
app.mount(
    "/", staticfiles.StaticFiles(directory=admin, html=True), name="admin",
)


def launch_http(host="0.0.0.0", port=8000, reload=False):
    logger.info(f"Launching http://{host}:{port}/")
    uvicorn.run(app, host=host, port=port, reload=reload)
