from fastapi import APIRouter, Body, HTTPException, status

from entitykb import rpc
from . import schema

router = APIRouter()
connection = rpc.RPCConnection()


# nodes


@router.get("/nodes/{key}", tags=["nodes"])
async def get_node(key: str) -> dict:
    """ Parse text and return document object. """
    async with connection as client:
        data = await client.call("get_node", key)
        if data is None:
            raise HTTP404(detail=f"Key [{key}] not found.")
        return data


@router.post("/nodes", tags=["nodes"])
async def save_node(node: dict = Body(...)) -> dict:
    """ Parse text and return document object. """
    async with connection as client:
        return await client.call("save_node", node)


@router.delete("/nodes/{key}/", tags=["nodes"])
async def remove_node(key: str):
    """ Remove node and relationships from KB. """
    async with connection as client:
        return await client.call("remove_node", key)


# # edges
#
#
# @abstractmethod
# def save_edge(self, edge):
#     """ Save edge to KB. """
#
#
# # queries
#


@router.post("/suggest", tags=["query"])
async def suggest(request: schema.SuggestRequest = Body(...)) -> schema.Doc:
    """ Parse text and return document object. """
    raise NotImplementedError


@router.post("/parse", tags=["query"])
async def parse(request: schema.ParseRequest = Body(...)) -> dict:
    """ Parse text and return document object. """
    async with connection as client:
        return await client.call("parse", request.text, *request.labels)


# admin


@router.post("/admin/commit", tags=["admin"])
async def commit() -> bool:
    """ Commit KB to disk. """
    async with connection as client:
        return await client.call("commit")


@router.post("/admin/clear", tags=["admin"])
async def clear() -> bool:
    """ Clear KB of all data. """
    async with connection as client:
        return await client.call("clear")


@router.post("/admin/reload", tags=["admin"])
async def reload() -> bool:
    """ Reload KB from disk. """
    async with connection as client:
        return await client.call("reload")


@router.post("/admin/info", tags=["admin"])
async def info() -> dict:
    """ Return KB's state and meta info. """
    async with connection as client:
        return await client.call("info")


class HTTP404(HTTPException):
    def __init__(self, detail: str, headers: dict = None):
        super(HTTP404, self).__init__(
            status.HTTP_404_NOT_FOUND, detail, headers
        )
