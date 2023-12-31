from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from pydantic import Field, PostgresDsn, SecretStr, RedisDsn
from pydantic_settings import BaseSettings


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

    user: str = Field('postgres', alias='POSTGRES_USER')
    password: str = Field('postgres', alias='POSTGRES_PASSWORD')
    database: str = Field('TimeInDataDB', alias='POSTGRES_DB')
    host: str = Field('localhost', alias='POSTGRES_HOST')
    port: int = Field(5432, alias='POSTGRES_PORT')

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

    token: SecretStr = Field(... , alias='TG_BOT_TOKEN')
    use_redis: bool = Field(False , alias='TG_BOT_USE_REDIS')


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

    redis_user: Optional[str] = Field(None, alias='REDIS_USER')
    redis_password: Optional[str] = Field(None, alias='REDIS_PASSWORD')
    redis_port: int = Field(6379, alias='REDIS_PORT')
    redis_host: str = Field('localhost', alias='REDIS_HOST')
    redis_path: str = Field('/0', alias='REDIS_PATH')

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


@dataclass
class Config:
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

    tg_bot: TgBotConfig
    db: DBConfig
    redis: RedisConfig


@lru_cache
def get_config() -> Config:
    """
    This function takes an optional file path as input and returns a Config object.

    :return: Config object with attributes set as per environment variables.
    """
    return Config(
        tg_bot=TgBotConfig(_env_file='.env'),
        db=DBConfig(),
        redis=RedisConfig(),
    )
