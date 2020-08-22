from entitykb import load, KB
from . import logger


class Singleton(object):
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = load()
        return cls._instance


def get_kb() -> KB:
    """
    Dependency function for FastAPI routes:
    https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-dependency
    """

    kb = None

    try:
        kb = Singleton.instance()
        yield kb

    finally:
        if kb and kb.is_dirty:
            logger.info("Changes found. Commit started.")
            kb.commit()
            logger.info("KB commit complete.")
        else:
            logger.info("No changes found. No KB commit.")
