import os
from functools import lru_cache

from loguru import logger
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


@lru_cache
def get_base_model_config() -> SettingsConfigDict:
    debug_mode: bool = os.environ.get('DEBUG', False) == '1'
    if debug_mode:
        logger.warning('DEBUG MODE ON!')

    return SettingsConfigDict(
        env_file='../.env' if debug_mode else '../prod.env',
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
    db : str
        The name of the database.
    port : int
        The port where the database server is listening.
    """
    model_config = get_base_model_config() | SettingsConfigDict(env_prefix='POSTGRES_')

    user: str = 'postgres'
    password: str = 'postgres'
    db: str = 'TimeInDataDB'
    server: str = 'localhost'
    port: int = 5432

    @property
    def url(self) -> str:
        """ Build a Postgres DSN from config. """
        return str(PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.server,
            port=self.port,
            path=self.db,
        ))


class APIConfig(BaseSettings):
    """
    API configuration class.

    Attributes
    ----------
    host : str
        The host on which the API will run
    port : int
        The host on which the API will listen
    """
    model_config = get_base_model_config() | SettingsConfigDict(env_prefix='API_')

    host: str = '127.0.0.1'
    port: int = 8000
    workers: int | None = None


class Config(BaseSettings):
    """
    The main configuration class that integrates all the other configuration classes.

    Attributes
    ----------
    api : APIConfig
        Holds the settings related to the api_service.
    db : DBConfig
        Holds the settings specific to the database.
    """
    model_config = get_base_model_config()

    debug: bool = 0

    api: APIConfig = APIConfig()
    db: DBConfig = DBConfig()


@lru_cache
def get_config() -> Config:
    """
    This function takes an optional file path as input and returns a Config object.

    :return: Config object with attributes set as per environment variables.
    """
    return Config()
