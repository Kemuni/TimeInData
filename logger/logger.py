import inspect
import logging
import sys

from loguru import logger

from logger.config import BaseLoggerConfig


class InterceptHandler(logging.Handler):
    """ Logging handler from loguru docs. """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
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


class LoggerCustomizer:
    """ Class for creating a custom logger and modifying existing ones. """

    @classmethod
    def init_loggers(cls, config: BaseLoggerConfig = BaseLoggerConfig()) -> None:
        """
        Function for creating loguru Logger objects with useful logs and modifying handler's of existing loggers

        :param config: A config file with logger settings.
        """
        cls.customize_existing_loggers()

        cls.replace_handlers(
            filepath=config.path,
            level=config.level,
            rotation=config.rotation,
            retention=config.retention,
            log_format=config.format,
        )

    @classmethod
    def replace_handlers(cls, filepath: str, level: str, rotation: str, retention: str, log_format: str) -> logger:
        """ Disconnect existing handlers and add our own, console and file """
        logger.remove()

        logger.add(
            sys.stdout,
            enqueue=True,
            backtrace=True,
            level=level.upper(),
            format=log_format
        )
        logger.add(
            filepath,
            rotation=rotation,
            retention=retention,
            enqueue=True,
            backtrace=True,
            level=level.upper(),
            format=log_format
        )

    @classmethod
    def customize_existing_loggers(cls, level: int = logging.INFO):
        """ Change handlers and log level for existing loggers """
        logging.basicConfig(handlers=[InterceptHandler()], level=level, force=True)
