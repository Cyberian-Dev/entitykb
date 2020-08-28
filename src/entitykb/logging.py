import logging.config

# using uvicorn's default formatter

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
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
