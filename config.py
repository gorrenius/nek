import os
from datetime import datetime

from starlette.config import Config
import logging
from logging.config import dictConfig
from pydantic import BaseModel

config = Config('env.env')

SCL_HOST = config("SCL_HOST", cast=str, default="localhost")
# SCL_PORT = config("SCL_PORT", cast=int, default=80)
SCL_USER = config("SCL_USER", cast=str, default="user")
SCL_PASS = config("SCL_PASS", cast=str, default="")

SCL_MAIN_PAGE = config("SCL_MAIN_PAGE", cast=str, default="")
SCL_IMBALANCE_PAGE = config("SCL_IMBALANCE_PAGE", cast=str, default="")
SCL_TIME_DELTA_DAYS = config("SCL_TIME_DELTA_DAYS", cast=int, default=1)
SCL_TIME_DELTA_DAYS_IMBALANCE = config("SCL_TIME_DELTA_DAYS_IMBALANCE", cast=int, default=1)
SCL_START_IMBALANCE_DATE = config("SCL_START_IMBALANCE_DATE", cast=str, default=datetime.today().replace(day=1))
SCL_PER_MONTH_MONTH = config("SCL_PER_MONTH_MONTH", cast=str, default="0")
SCL_PER_MONTH_YEAR = config("SCL_PER_MONTH_YEAR", cast=str, default="0")

PG_HOST = config("PG_HOST", cast=str, default="localhost")
PG_PORT = config("PG_PORT", cast=int, default=54321)
PG_USER = config("PG_USER", cast=str, default="user")
PG_PASS = config("PG_PASS", cast=str, default="")
PG_DB = config("PG_DB", cast=str, default="energy")
DEFAULT_SCHEMA = config("DEFAULT_SCHEMA", cast=str, default="consumer")
# CONTROL_SCHEMA = config("CONTROL_SCHEMA", cast=str, default="control")
# SCADA_SCHEMA = config("SCADA_SCHEMA", cast=str, default="scada")

USE_SSH = config("USE_SSH", cast=bool, default=False)
SSH_HOST = config("SSH_HOST", cast=str, default="localhost")
SSH_PORT = config("SSH_PORT", cast=int, default=22)
SSH_USER = config("SSH_USER", cast=str, default="user")
SSH_PASS = config("SSH_PASS", cast=str, default="pass")

DIR_LOG = config("DIR_LOG", cast=str, default="../log")


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "mms"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "console": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s | %(asctime)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "file": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelname)s | %(asctime)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    }
    handlers = {
        "console": {
            "formatter": "console",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "file",
            "filename": os.path.join(DIR_LOG, "mms.log"),
            "maxBytes": 1024 * 1024 * 1024,
            "backupCount": 3,
        },
    }
    loggers = {
        LOGGER_NAME: {"handlers": ["file"], "level": LOG_LEVEL},
    }


dictConfig(LogConfig().dict())
logger = logging.getLogger("mms")
