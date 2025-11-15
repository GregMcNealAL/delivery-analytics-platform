import logging
from logging.config import dictConfig


def setup_logging():
    dictConfig({
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
            },
            "uvicorn": {
                "format": "%(levelprefix)s %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "INFO",
            }
        },
        "loggers": {
            "analytics": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn.error": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False
            }
        }
    })

    logging.getLogger("analytics").info("Logging initialized.")
