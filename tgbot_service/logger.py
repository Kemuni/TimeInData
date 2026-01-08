import inspect
import logging
import sys
from typing import Iterable

from loguru import logger

LOGGER_FORMAT: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )


class InterceptHandler(logging.Handler):
    """ Intercept standard logging messages and redirect them to loguru. """
    def emit(self, record: logging.LogRecord) -> None:
        # Get the corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def configure_logger(level: int = logging.INFO, supress_loggers: Iterable[str] = []) -> None:
    """ Configure logger with custom format and intercept handler """
    logger.remove()

    logger.add(
        sys.stdout,
        level=level,
        format=LOGGER_FORMAT,
        colorize=True,
        backtrace=True,
        diagnose=True,
        serialize=False,
        enqueue=True
    )
    logging.basicConfig(handlers=[InterceptHandler()], level=level, force=True)

    for logger_name in supress_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    logger.info(f"Logger configured: level={level}, supress_loggers={supress_loggers}")
