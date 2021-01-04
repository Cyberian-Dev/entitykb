from typing import List

from fastapi import APIRouter, Body, security, Depends

from entitykb import (
    rpc,
    Doc,
    models,
    Config,
    Entity,
    Direction,
    exceptions,
    User,
    UserToken,
)

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
            raise exceptions.HTTP404(detail=f"Key [{key}] not found.")
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


@router.get(
    "/nodes/{key}/neighbors", tags=["nodes"], response_model=List[models.Node]
)
async def get_neighbors(
    key: str,
    verb: str = None,
    label: str = None,
    direction: Direction = None,
    limit: int = 100,
) -> List[models.Node]:
    """ Return list of neighbor nodes for a given node. """
    request = models.EdgeRequest(
        node_key=key, verb=verb, label=label, direction=direction, limit=limit
    )
    async with connection as client:
        data = await client.call("get_neighbors", request.dict())
        return data


@router.get("/nodes/{key}/edges", tags=["nodes"])
async def get_edges(
    key: str, verb: str = None, direction: Direction = None, limit: int = 100
):
    """ Return list of edges for a given node. """
    request = models.EdgeRequest(
        node_key=key, verb=verb, direction=direction, limit=limit
    )
    async with connection as client:
        data = await client.call("get_edges", request.dict())
        return data


# edges


@router.post("/edges", tags=["edges"])
async def save_edge(edge: models.IEdge = Body(...)) -> models.IEdge:
    """ Save edge to graph store. """
    async with connection as client:
        return await client.call("save_edge", edge.dict())


# pipeline


@router.post("/parse", tags=["pipeline"], response_model=Doc)
async def parse(request: models.ParseRequest = Body(...)) -> Doc:
    """ Parse text and return document object. """
    async with connection as client:
        data = await client.call("parse", request.dict())
        return data


@router.post("/find", tags=["pipeline"], response_model=List[Entity])
async def find(request: models.ParseRequest = Body(...)) -> List[Entity]:
    """ Parse text and return found entities. """
    async with connection as client:
        data = await client.call("find", request.dict())
        return data


@router.post("/find_one", tags=["pipeline"], response_model=Entity)
async def find_one(request: models.ParseRequest = Body(...)) -> Entity:
    """ Parse text and return entity, if one and only one found. """
    async with connection as client:
        data = await client.call("find_one", request.dict())
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


# users

oauth2_scheme = security.OAuth2PasswordBearer(tokenUrl="token")


async def get_user_by_token(token: str = Depends(oauth2_scheme)) -> User:
    async with connection as client:
        user = await client.call("get_user", token)

    if not user:
        raise exceptions.HTTP401(
            detail="Invalid user token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/token", tags=["users"], response_model=UserToken)
async def login_for_access_token(
    form_data: security.OAuth2PasswordRequestForm = Depends(),
):
    async with connection as client:
        access_token = await client.call(
            "authenticate", form_data.username, form_data.password
        )

    if not access_token:
        raise exceptions.HTTP401(
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserToken(access_token=access_token, token_type="bearer")


@router.get("/user", tags=["users"], response_model=User)
async def get_user(user: User = Depends(get_user_by_token)):
    if not user:
        raise exceptions.HTTP401(
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
