
import sys
from urllib.parse import parse_qs

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from loguru import logger


def setup_logging():
    log_level = "INFO"
    logger.remove()
    logger.add(
        "logs/app.log",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} | {message}",
        rotation="5 MB",
        retention=10,
    )
    logger_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    logger.add(
        sys.stdout,
        level=log_level,
        colorize=True,
        format=logger_format,
    )