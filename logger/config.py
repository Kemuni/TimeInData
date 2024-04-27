import logging
from enum import Enum

from pydantic_settings import BaseSettings


class LoggerLevel(str, Enum):
    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'


class BaseLoggerConfig(BaseSettings):
    """
    Logger configuration class.

    Attributes
    ----------
    path : str
        The path to file with logs.
    level : LoggerLevel
        The level of logs.
    rotation: str
        The rotation of logs. For example: "2 days" means that one *.logs file keep logs only for last 2 days.
    retention: str
        The retention of logs. For example: "1 months" means that *.logs file older than 1 month will be deleted.
    format: str
        The format of logs.
    """

    path: str = "logs/logs.log"
    level: LoggerLevel = LoggerLevel.INFO
    rotation: str = "20 days"
    retention: str = "1 months"
    format: str = (
        "<level>{level: <8}</level> <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> - <cyan>{name}</cyan>:"
        "<cyan>{function}</cyan> - <level>{message}</level>"
    )
