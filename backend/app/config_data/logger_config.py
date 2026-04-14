import os

from loguru import logger

logger.remove()

os.makedirs("logs", exist_ok=True)

logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    format="{time:HH:mm:ss} | {level} | {message}",
    level="DEBUG",
    rotation="10 MB",
    retention="30 days",
    encoding="utf-8",
)

logger.add(
    lambda msg: print(msg, end=""),
    format="{time:HH:mm:ss} | {level} | {message}",
    level="INFO",
)

__all__ = ["logger"]
