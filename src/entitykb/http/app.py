from pathlib import Path

from fastapi import FastAPI, staticfiles
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from . import routes

app = FastAPI(
    title="EntityKB HTTP API",
    description="EntityKB HTTP API",
    default_response_class=JSONResponse,
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
admin = Path(__file__).parent / "admin/public"
app.mount(
    "/",
    staticfiles.StaticFiles(directory=admin, html=True),
    name="admin",
)


@app.exception_handler(ConnectionRefusedError)
async def rpc_connection_handler(*_):
    return JSONResponse(
        status_code=503,
        content="Connection Refused. Check RPC server.",
    )
