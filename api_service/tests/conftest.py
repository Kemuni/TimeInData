from typing import Generator, AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from testcontainers.postgres import PostgresContainer

from database.models import Base
from database.repositories import DatabaseRepo
from dependencies import get_db


@pytest.fixture(scope="session")
def postgres_container_url() -> Generator[str, None, None]:
    """ Run Postgres in Docker container and return connection URL """
    with PostgresContainer("postgres:17") as container:
        url = container.get_connection_url().replace("psycopg2", "asyncpg")
        yield url


@pytest.fixture(scope="session")
async def db_engine(postgres_container_url: str) -> AsyncGenerator[AsyncEngine, None]:
    """ Create SQLAlchemy engine and tables in test DB. Drop tables after all tests """
    engine = create_async_engine(postgres_container_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """ Clear database and create test session to interact with DB """
    async with db_engine.begin() as conn:
        # Очистка данных без пересоздания таблиц
        tables = await conn.run_sync(lambda sync_conn: Base.metadata.sorted_tables)
        for table in tables:
            await conn.execute(text(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE"))

    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )

    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
def app() -> Generator[FastAPI, None, None]:
    from app import app

    yield app


@pytest.fixture
async def async_client(app: FastAPI, db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """ Override `get_db` dependency in application and return FastAPI test client """
    def override_get_db() -> DatabaseRepo:
        return DatabaseRepo(session=db_session)

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
