from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.database import get_db
from app.models.cart import CartItem
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemOut

# Псевдонимы типов
DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post(
   "/", 
   response_model=CartItemOut,
   status_code=status.HTTP_201_CREATED,
   summary="Добавить товары в корзину"
   )
async def add_to_cart(
    item_data: CartItemCreate, 
    db: DBSession,
    current_user: CurrentUser # Только для залогиненных!
) -> CartItem:
    """
    Добавляет новый товар в корзину текущего пользователя.

    Args:
        item_data: Схема данных добавляемого товара.
        db: Асинхронная сессия базы данных.
        current_user: Объект текущего авторизованного пользователя.

    Returns:
        Объект CartItem с подгруженными данными о продукте.
    """
    new_item = CartItem(user_id=current_user.id, **item_data.model_dump())
    db.add(new_item)
    await db.commit()

    query = select(CartItem
                   ).where(CartItem.id == new_item.id
                           ).options(selectinload(CartItem.product))
    result = await db.execute(query)
    return result.scalars().first()

@router.get(
    "/", 
    response_model=list[CartItemOut],
    summary="Получить корзину пользователя"
)
async def get_my_cart(
    db: DBSession,
    current_user: CurrentUser
) -> CartItem:
    """
    Возвращает список всех товаров в корзине текущего пользователя.

    Args:
        db: Асинхронная сессия базы данных.
        current_user: Объект текущего авторизованного пользователя.

    Returns:
        Список объектов CartItem с информацией о продуктах.
    """
    query =select(CartItem
                  ).where(CartItem.user_id == current_user.id
                          ).options(selectinload(CartItem.product))
    result = await db.execute(query)
    return result.scalars().all()
