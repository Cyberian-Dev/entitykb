import os
from fastapi import FastAPI, staticfiles, APIRouter
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import UJSONResponse

from . import read, write

app = FastAPI(
    title="EntityKB API",
    description="EntityKB: Application Programming Interface (API)",
    default_response_class=UJSONResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount Admin UI
ui_public_dir = os.path.join(os.path.dirname(__file__), "admin_ui/public")
app.mount(
    "/",
    staticfiles.StaticFiles(directory=ui_public_dir, html=True),
    name="ui_public_dir",
)

# add API routes
api_router = APIRouter()
api_router.include_router(read.router, prefix="/r", tags=["read-only"])
api_router.include_router(write.router, prefix="/w", tags=["write"])
app.include_router(api_router)
