import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.main import app
from app.db.database import Base
from app.core.config import settings

from tests.integration.factories import create_order_factory, create_outbox_event_factory

@pytest.fixture
def order_factory(db_session):
    """Factory de orders que já usa a sessão do teste"""
    async def _factory(customer_name: str, address: str):
        return await create_order_factory(customer_name, address, db_session)
    return _factory

@pytest.fixture
def outbox_factory(db_session):
    """Factory de eventos outbox que já usa a sessão do teste"""
    async def _factory(order_id=None, event_type="OrderCreated", payload=None, sent=False):
        return await create_outbox_event_factory(order_id, event_type, payload, sent, db_session)
    return _factory


@pytest.fixture(scope="function")
async def engine():
    engine = create_async_engine(
        settings.database_url, future=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(engine):
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        yield session
        await session.rollback()

# ------------- CLEAN DATABASE -------------
@pytest.fixture(autouse=True, scope="function")
async def clean_db(db_session):
    """
    Limpa o banco antes de cada teste.
    """
    tables = ["outbox_events", "order_events", "orders"]
    for table in tables:
        await db_session.execute(text(f"DELETE FROM {table}"))
    await db_session.commit()
    yield

@pytest.fixture(scope="function")
async def client(db_session):
    """Client HTTP que usa a mesma sessão de teste."""
    app.state.db_session = db_session

    async with AsyncClient(base_url="http://app:8000") as ac:
        yield ac