from fastapi import APIRouter, Body, HTTPException, status

from entitykb import rpc, Doc, models, Config

router = APIRouter()
connection = rpc.RPCConnection()
config = Config.create()


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
    """ Saves nodes to graph and terms to index. """
    async with connection as client:
        return await client.call("save_node", node)


@router.delete("/nodes/{key}/", tags=["nodes"])
async def remove_node(key: str):
    """ Remove node and relationships from KB. """
    async with connection as client:
        return await client.call("remove_node", key)


# edges


@router.post("/edges", tags=["edges"])
async def save_edge(edge: dict = Body(...)) -> dict:
    """ Save edge to graph store. """
    async with connection as client:
        return await client.call("save_edge", edge)


# pipeline


@router.post("/parse", tags=["pipeline"], response_model=Doc)
async def parse(request: models.ParseRequest = Body(...)) -> Doc:
    """ Parse text and return document object. """
    async with connection as client:
        data = await client.call("parse", request.dict())
        return data


# graph


@router.post("/search", tags=["graph"], response_model=models.SearchResponse)
async def search(request: models.SearchRequest = Body(...)):
    """ Parse text and return document object. """
    async with connection as client:
        data = await client.call("search", request.dict())
        return data


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


# meta


@router.get("/meta/info", tags=["meta"])
async def info() -> dict:
    """ Return KB's state and meta info. """
    async with connection as client:
        return await client.call("info")


@router.get("/meta/schema", tags=["meta"])
async def get_schema() -> dict:
    async with connection as client:
        return await client.call("get_schema")


class HTTP404(HTTPException):
    def __init__(self, detail: str, headers: dict = None):
        super(HTTP404, self).__init__(
            status.HTTP_404_NOT_FOUND, detail, headers
        )
