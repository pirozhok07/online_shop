import asyncio
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_db.db"

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread":False},
    poolclass=StaticPool,
    )

TestingSessionLocal = async_sessionmaker(
    bind=engine_test, 
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Заменяет основную зависимость базы данных на тестовую.
    """
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    """
    Создает и управляет циклом событий (event loop) для всей тестовой сессии.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def init_db() -> AsyncGenerator[None, None]:
    """
    Автоматически подготавливает БД перед каждым тестом.
    
    Создает таблицы перед началом теста и удаляет их после завершения,
    чтобы обеспечить изоляцию данных между тестами.
    """
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Инициализирует асинхронный HTTP-клиент для тестирования эндпоинтов.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
