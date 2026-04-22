from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


engine = create_async_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.
    Использует новый стиль DeclarativeBase (SQLAlchemy 2.0+).
    """
    pass

async def get_db()-> AsyncGenerator[AsyncSession, None]:
    """
    Асинхронная зависимость (Dependency Injection) для получения сессии БД.

    Гарантирует закрытие сессии после завершения обработки запроса.

    Yields:
        AsyncSession: Объект асинхронной сессии базы данных.
    """
    async with AsyncSessionLocal() as session:
        yield session
