import os
from functools import lru_cache
from typing import Optional

from loguru import logger
from pydantic import PostgresDsn, SecretStr, RedisDsn
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


class DBConfig(BaseSettings):
    """
    Database configuration class.
    This class holds the settings for the database, such as host, password, port, etc.

    Attributes
    ----------
    host : str
        The host where the database server is located.
    password : str
        The password used to authenticate with the database.
    user : str
        The username used to authenticate with the database.
    database : str
        The name of the database.
    port : int
        The port where the database server is listening.
    """
    model_config = get_base_model_config() | SettingsConfigDict(env_prefix='POSTGRES_')

    user: str = 'postgres'
    password: str = 'postgres'
    database: str = 'TimeInDataDB'
    host: str = 'localhost'
    port: int = 5432

    @property
    def dsn(self) -> PostgresDsn:
        """ Build a Postgres DSN from config. """
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            path=self.database,
        )


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
    def dsn(self) -> RedisDsn:
        """ Constructs and returns a Redis DSN (Data Source Name) for this database configuration. """
        return RedisDsn.build(
            scheme='redis',
            username=self.redis_user,
            password=self.redis_password,
            host=self.redis_host,
            port=self.redis_port,
            path=self.redis_path
        )


class Config(BaseSettings):
    """
    The main configuration class that integrates all the other configuration classes.

    Attributes
    ----------
    tg_bot : TgBotConfig
        Holds the settings related to the Telegram Bot.
    db : DBConfig
        Holds the settings specific to the database.
    redis : RedisConfig
        Holds the settings specific to Redis.
    """
    model_config = get_base_model_config()

    tg_bot: TgBotConfig = TgBotConfig()
    db: DBConfig = DBConfig()
    redis: RedisConfig = RedisConfig()


@lru_cache
def get_config() -> Config:
    """
    This function takes an optional file path as input and returns a Config object.

    :return: Config object with attributes set as per environment variables.
    """
    return Config()
