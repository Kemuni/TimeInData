from collections.abc import AsyncGenerator
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
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
async def db_engine(postgres_container_url: str) -> AsyncGenerator[AsyncEngine, None, None]:
    """ Create SQLAlchemy engine and tables in test DB. Drop tables after all tests """
    engine = create_async_engine(postgres_container_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None, None]:
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
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture
def app() -> Generator[FastAPI, None, None]:
    from app import app

    yield app


@pytest.fixture
def client(db_session: AsyncSession, app: FastAPI) -> Generator[TestClient, None, None]:
    """ Override `get_db` dependency in application and return FastAPI test client """
    def override_get_db() -> DatabaseRepo:
        return DatabaseRepo(session=db_session)

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
