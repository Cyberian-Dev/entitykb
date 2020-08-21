from entitykb import LabelSet, KB, load

from .logger import logger


def get_kb() -> KB:
    """
    Dependency function for FastAPI routes:
    https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-dependency
    """
    kb = load()
    logger.info(f"Knowledge Base loaded: {kb.config.root_dir}")

    try:
        yield kb

    finally:
        if kb.is_dirty:
            logger.info("Changes found. Commit started.")
            kb.commit()
            logger.info("KB commit complete.")
        else:
            logger.info("No changes found. No KB commit.")


from .app import app

__all__ = ("app", "logger", "LabelSet", "KB", "load", "get_kb")
