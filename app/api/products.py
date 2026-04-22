from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductBase, ProductOut, ProductPagination

# Псевдонимы типов
DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentAdmin = Annotated[User, Depends(get_current_admin)]

router = APIRouter(prefix="/products", tags=["products"])


@router.get(
    "/", 
    response_model=ProductPagination,
    summary="Получить список товаров"
)
async def get_products(
    db: DBSession,
    category: str | None = None,
    min_price: float = 0,
    max_price: float = 1_000_000,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
) -> dict[str, Any]:
    """
    Возвращает список товаров с фильтрацией и пагинацией.

    Args:
        db: Асинхронная сессия базы данных.
        category: Фильтр по категории.
        min_price: Минимальная цена.
        max_price: Максимальная цена.
        page: Номер страницы (начиная с 1).
        size: Количество товаров на странице.

    Returns:
        Словарь с товарами, общим количеством и данными пагинации.
    """
    skip = (page - 1) * size

    stmt = select(Product).where(
        Product.price >= min_price, 
        Product.price <= max_price
    )
    if category:
        stmt = stmt.where(Product.category == category)
    
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one() or 0

    stmt = stmt.offset(skip).limit(size)
    result = await db.execute(stmt)
    items = result.scalars().all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size
    }

@router.post(
    "/", 
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый товар",
    responses={
        403: {"description": "Доступ запрещен: требуется роль администратора"},
        401: {"description": "Пользователь не авторизован"}
    }
)
async def create_product(
    product_data: ProductBase, 
    db: DBSession,
    admin: CurrentAdmin
) -> Product:
    """
    Добавляет новый товар в базу данных.
    
    Args:
        product_data: Объект текущего товара.
        db: Асинхронная сессия базы данных.
        admin: Авторизация с правами администратора

    Returns:
        Объект товара Product.
    """
    new_product = Product(**product_data.model_dump())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product
