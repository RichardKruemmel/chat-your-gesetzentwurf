import logging
import logging.config


def configure_logging():
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "formatter": "standard",
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "": {"handlers": ["default"], "level": "INFO", "propagate": True},
        },
    }

    logging.config.dictConfig(logging_config)
