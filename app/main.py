from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.core.security import get_password_hash
from fastapi import FastAPI, Response, status
from sqlalchemy import select

from app.api import auth, cart, orders, products
from app.core.logger import logger
from app.database import AsyncSessionLocal, engine
from app.models import Base
from app.models.user import User
from app.core.config import settings

@asynccontextmanager
async def lifespan(
    app: FastAPI
) -> AsyncGenerator[None, None]:
    """
    Управляет жизненным циклом приложения.
    
    Выполняет инициализацию ресурсов при запуске (создание таблиц) 
    и очистку при завершении работы.
    """
    if settings.CREATE_TABLES_ON_START:
        logger.info("Инициализация базы данных...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # Проверяем, есть ли хоть один пользователь
        result = await session.execute(select(User).limit(1))
        user_exists = result.scalars().first()

        if not user_exists:
            logger.info("Создание суперпользователя по умолчанию...")
            new_admin = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                is_admin=True  # Убедись, что в модели User есть это поле
            )
            session.add(new_admin)
            await session.commit()
            logger.info(f"Админ создан: {settings.FIRST_SUPERUSER_EMAIL}")
            
    logger.info("Приложение Shop API успешно запущено")
    yield

    logger.info("Приложение Shop API завершает работу")
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API для управления магазином: товары, корзина и заказы",
    version=settings.PROJECT_VERSION,
    lifespan=lifespan
)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """
    Корневой эндпоинт для проверки работоспособности API.
    """
    return {"message": f"Welcome to the {settings.PROJECT_NAME}"}

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)