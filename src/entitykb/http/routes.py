from typing import List
from urllib.parse import unquote

from fastapi import APIRouter, Body, security, Depends

from entitykb import (
    ProxyKB,
    models,
    Config,
    Direction,
    exceptions,
    User,
    UserToken,
)

router = APIRouter()
config = Config.create()
kb = ProxyKB()


# nodes


@router.get("/nodes/{key}", tags=["nodes"])
def get_node(key: str) -> dict:
    """ Parse text and return document object. """
    key = unquote(key)
    return kb.get_node(key)


@router.post("/nodes", tags=["nodes"])
async def save_node(node: dict = Body(...)) -> dict:
    """ Saves nodes to graph and terms to index. """
    return kb.save_node(node)


@router.delete("/nodes/{key}/", tags=["nodes"])
async def remove_node(key: str):
    """ Remove node and relationships from KB. """
    key = unquote(key)
    return kb.remove_node(key)


@router.post(
    "/nodes/neighbors",
    tags=["nodes"],
    response_model=models.NeighborResponse,
)
async def get_neighbors(
    request: models.NeighborRequest,
) -> List[dict]:
    """ Return list of neighbor nodes for a given node. """
    return kb.get_neighbors(
        request.node_key,
        request.verb,
        request.direction,
        request.label,
        request.offset,
        request.limit,
    )


@router.get("/nodes/{key}/edges", tags=["nodes"])
async def get_edges(
    key: str, verb: str = None, direction: Direction = None, limit: int = 100
) -> List[dict]:
    key = unquote(key)
    return kb.get_edges(key, verb, direction, limit)


@router.post("/nodes/count", tags=["nodes"])
async def count_nodes(request: models.CountRequest) -> int:
    return kb.count_nodes(request.term, request.labels)


# edges


@router.post("/edges", tags=["edges"])
async def save_edge(edge: models.IEdge = Body(...)) -> dict:
    """ Save edge to graph store. """
    return kb.save_edge(edge.dict())


# pipeline


@router.post("/parse", tags=["pipeline"])
async def parse(request: models.ParseRequest = Body(...)) -> dict:
    """ Parse text and return document object. """
    return kb.parse(request.text, request.labels, request.pipeline)


@router.post("/find", tags=["pipeline"], response_model=List[dict])
async def find(request: models.ParseRequest = Body(...)) -> List[dict]:
    """ Parse text and return found entities. """
    return kb.find(request.text, request.labels, request.pipeline)


@router.post("/find_one", tags=["pipeline"], response_model=dict)
async def find_one(request: models.ParseRequest = Body(...)) -> dict:
    """ Parse text and return entity, if one and only one found. """
    return kb.find_one(request.text, request.labels, request.pipeline)


# graph


@router.post("/search", tags=["graph"], response_model=models.SearchResponse)
async def search(request: models.SearchRequest = Body(...)):
    """ Parse text and return document object. """
    return kb.search(
        request.q,
        request.labels,
        request.keys,
        request.traversal,
        request.limit,
        request.offset,
    )


# admin


@router.post("/admin/reload", tags=["admin"])
async def reload() -> bool:
    """ Reload KB from disk. """
    return kb.reload()


@router.get("/meta/info", tags=["meta"])
async def info() -> dict:
    """ Return KB's state and meta info. """
    return kb.info()


@router.get("/meta/schema", tags=["meta"])
async def get_schema() -> dict:
    return kb.get_schema()


# users

oauth2_scheme = security.OAuth2PasswordBearer(tokenUrl="token")


async def get_user_by_token(token: str = Depends(oauth2_scheme)) -> User:
    user = kb.get_user(token)

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
    access_token = kb.authenticate(form_data.username, form_data.password)

    if not access_token:
        raise exceptions.HTTP401(
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserToken(access_token=access_token, token_type="bearer")


@router.get("/user", tags=["users"], response_model=User)
async def get_user(user: User = Depends(get_user_by_token)):
    return user
