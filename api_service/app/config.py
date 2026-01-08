import os
from functools import lru_cache
from urllib.parse import quote

from loguru import logger
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


@lru_cache
def get_base_model_config() -> SettingsConfigDict:
    debug_mode: bool = os.environ.get('DEBUG', False) == '1'
    if debug_mode:
        logger.warning('DEBUG MODE ON!')

    return SettingsConfigDict(
        env_file='../.env' if debug_mode else '../.env.production',
        env_nested_delimiter='__',
        extra='ignore',
    )


class DBConfig(BaseSettings):
    """
    Database configuration class.
    This class holds the settings for the database, such as host, password, port, etc.

    Attributes
    ----------
    server : str
        The host where the database server is located.
    password : str
        The password used to authenticate with the database.
    user : str
        The username used to authenticate with the database.
    db : str
        The name of the database.
    port : int
        The port where the database server is listening to.
    """
    model_config = get_base_model_config() | SettingsConfigDict(env_prefix='POSTGRES_')

    user: str = 'postgres'
    password: str = 'postgres'
    db: str = 'TimeInDataDB'
    server: str = 'localhost'
    port: int = 5432
    job_store_db: str = 'TimeInDataJobStoreDB'

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

    @property
    def job_store_url(self) -> str:
        return str(PostgresDsn.build(
            scheme="postgresql",
            username=self.user,
            password=self.password,
            host=self.server,
            port=self.port,
            path=self.job_store_db,
        ))


class RabbitMQConfig(BaseSettings):
    """
    RabbitMQ configuration class.
    Contain all settings for RabbitMQ.

    Attributes
    ----------
    username: str
        The username of account for connecting to the broker.
    password: str
        The password of account for connecting to the broker.
    host: str
        The host where the broker is located.
    port: int
        The port of broker.
    vhost: str
        The virtual host to connect to (for task isolation).
    reminder_queue_name: str
        The name of the queue for reminders.
    """
    model_config = get_base_model_config() | SettingsConfigDict(env_prefix='RABBITMQ_')

    username: str = 'guest'
    password: str = 'guest'
    host: str = 'localhost'
    port: int = 5672
    vhost: str = 'time_in_data_vhost'

    reminder_queue_name: str = 'reminder_queue'

    @property
    def url(self) -> str:
        """ Build a RabbitMQ DSN from config. """
        return f"amqp://{self.username}:{quote(self.password)}@{self.host}:{self.port}/{self.vhost}"


class APIConfig(BaseSettings):
    """
    API configuration class.

    Attributes
    ----------
    host : str
        The host on which the API will run
    port : int
        The host on which the API will listen to
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
    rabbitmq : RabbitMQConfig
        Holds the settings for the RabbitMQ.
    """
    model_config = get_base_model_config()

    debug: bool = 0

    api: APIConfig = APIConfig()
    db: DBConfig = DBConfig()
    rabbitmq: RabbitMQConfig = RabbitMQConfig()


@lru_cache
def get_config() -> Config:
    """
    This function takes an optional file path as input and returns a Config object.

    :return: Config object with attributes set as per environment variables.
    """
    return Config()
