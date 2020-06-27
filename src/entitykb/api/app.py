import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import UJSONResponse

from .instance import Instance
from .routes import router

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
app.include_router(router)

logger = logging.getLogger("api")


@app.on_event("startup")
def startup_event():
    kb = Instance.get()
    logger.info(f"Knowledge Base loaded: {kb.config.root_dir}")


@app.on_event("shutdown")
def shutdown_event():
    kb = Instance.get()

    if kb.is_dirty:
        logger.info(f"Changes found. Commit started: {kb.index.index_path}")
        kb.commit()
        logger.info("KB commit complete.")
    else:
        logger.info("No changes found. No KB commit.")
