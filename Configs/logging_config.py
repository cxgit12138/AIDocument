import logging
import logging.config
from pathlib import Path

# 日志配置
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s %(name)s %(process)d:%(lineno)d %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(asctime)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "./Logs/app.log",
            "maxBytes": 1024 * 1024 * 10,  # 10MB
            "backupCount": 5,
            "formatter": "default",
        }
    },
    "loggers": {
        "": {"handlers": ["default", "file"], "level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
        "file_review": {"handlers": ["default", "file"], "level": "INFO"},
        "rar_analysis": {"handlers": ["default", "file"], "level": "INFO"},
    },
}


def setup_logging():
    """设置日志配置"""
    # 创建日志目录
    log_dir = Path("./Logs")
    log_dir.mkdir(exist_ok=True)

    # 应用日志配置
    logging.config.dictConfig(LOGGING_CONFIG)

    return logging.getLogger(__name__)
