import inspect
import json
import logging
import sys
from pathlib import Path

from loguru import logger


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
    def init_loggers(cls, config_path: Path = Path('logger', 'config.json')) -> None:
        """
        Function for creating loguru Logger objects with useful logs and modifying handler's of existing loggers

        :param config_path: A path to json-file with logger settings.
        """
        config = cls.load_logging_config(config_path)
        logging_config = config.get('logger')

        cls.customize_existing_loggers()

        cls.replace_handlers(
            filepath=logging_config.get('path'),
            level=logging_config.get('level'),
            retention=logging_config.get('retention'),
            rotation=logging_config.get('rotation'),
            log_format=logging_config.get('format')
        )

    @classmethod
    def replace_handlers(cls, filepath: Path, level: str, rotation: str, retention: str, log_format: str) -> None:
        """ Disconnect existing handlers and add our own, for console and file """
        logger.remove()

        logger.add(
            sys.stdout,
            enqueue=True,
            backtrace=True,
            level=level.upper(),
            format=log_format
        )
        logger.add(
            str(filepath),
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

    @classmethod
    def load_logging_config(cls, config_path: Path) -> dict:
        """
        Read config json-file for loggers.

        :param config_path: Path to config json-file.
        :return: Dict with logger config.
        """
        with open(config_path) as config_file:
            config = json.load(config_file)
        return config
