import os

from fastapi import FastAPI, staticfiles
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import UJSONResponse

from . import routes

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


app.include_router(routes.router)

# mount Admin UI
admin = os.path.join(os.path.dirname(__file__), "admin/public")
app.mount(
    "/", staticfiles.StaticFiles(directory=admin, html=True), name="admin",
)


@app.exception_handler(ConnectionRefusedError)
async def rpc_connection_handler(*_):
    return UJSONResponse(
        status_code=503, content="Connection Refused. Check RPC server.",
    )
