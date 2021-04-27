import logging.config
import time
from functools import wraps


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "entitykb.deps.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": True,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {"entitykb": {"handlers": ["default"], "level": "INFO"}},
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("entitykb")
logger.setLevel("INFO")


def timed(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.time()

        try:
            result = f(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
            raise e

        lapse = time.time() - start
        logger.info(f"{f.__qualname__}: {lapse:.4f}")
        return result

    return wrapper


logger.timed = timed
