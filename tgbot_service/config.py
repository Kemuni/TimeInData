import os
from functools import lru_cache
from typing import Optional

from loguru import logger
from pydantic import SecretStr, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


@lru_cache
def get_base_model_config() -> SettingsConfigDict:
    debug_mode: bool = os.environ.get('DEBUG', False) == '1'
    if debug_mode:
        logger.warning('DEBUG MODE ON!')

    return SettingsConfigDict(
        env_file='.env' if debug_mode else 'prod.env',
        env_nested_delimiter='__',
        extra='ignore',
    )


class APISettings(BaseSettings):
    """
    API configuration class.
    This class holds the settings for communication with the API service.

    Attributes
    ----------
    domain : str
        The domain of API service.
    port : port
        The port of API service.
    """
    model_config = get_base_model_config() | SettingsConfigDict(env_prefix='API_')

    domain: str = '127.0.0.1'
    port: int = 8000


class TgBotConfig(BaseSettings):
    """
    Telegram bot configuration class.
    This class holds the settings for the bot.

    Attributes
    ----------
    token : str
        The token which we get from telegram BotFather.
    use_redis : str
        Boolean variable that indicates whether we are using redis.
    """
    model_config = get_base_model_config() | SettingsConfigDict(env_prefix='TG_BOT_')

    token: SecretStr
    use_redis: bool = False


class MessagesTextConfig(BaseSettings):
    """
    Message text configuration class.
    This class holds status messages for user.
    """
    model_config = get_base_model_config() | SettingsConfigDict(env_prefix='MESSAGE_TEXT_')

    error: str = "⚠️ Something went wrong. Try again later!"


class RedisConfig(BaseSettings):
    """
    Redis configuration class.

    Attributes
    ----------
    redis_user : Optional(str)
        The username used to authenticate with Redis.
    redis_password : Optional(str)
        The password used to authenticate with Redis.
    redis_host : str
        The host where Redis server is located.
    redis_port : int
        The port where Redis server is listening.
    redis_path : str
        The path where Redis server is located.
    """
    model_config = get_base_model_config() | SettingsConfigDict(env_prefix='REDIS_')

    redis_user: Optional[str] = None
    redis_password: Optional[str] = None
    redis_port: int = 6379
    redis_host: str = 'localhost'
    redis_path: str = '/0'

    @property
    def url(self) -> str:
        """ Constructs and returns a Redis DSN (Data Source Name) for this database configuration. """
        return str(RedisDsn.build(
            scheme='redis',
            username=self.redis_user,
            password=self.redis_password,
            host=self.redis_host,
            port=self.redis_port,
            path=self.redis_path
        ))


class Config(BaseSettings):
    """
    The main configuration class that integrates all the other configuration classes.

    Attributes
    ----------
    tg_bot : TgBotConfig
        Holds the settings related to the Telegram Bot.
    msg_texts : MessagesTextConfig
        Holds the status messages for telegram bot.
    api : APISettings
        Holds the settings to communicate with API service.
    redis : RedisConfig
        Holds the settings specific to Redis.
    """
    model_config = get_base_model_config()

    debug: bool = 0
    tg_bot: TgBotConfig = TgBotConfig()
    msg_texts: MessagesTextConfig = MessagesTextConfig()
    api: APISettings = APISettings()
    redis: RedisConfig = RedisConfig()


@lru_cache
def get_config() -> Config:
    """
    This function takes an optional file path as input and returns a Config object.

    :return: Config object with attributes set as per environment variables.
    """
    return Config()
