from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.logger import logger
from app.database import get_db
from app.models.cart import CartItem
from app.models.order import Order
from app.models.user import User

# Псевдонимы типов
DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get(
    "/checkout",
    summary="Оформить заказ",
    status_code=status.HTTP_201_CREATED,
    response_description="Информация о созданном заказе"
)
async def checkout(
    db: DBSession,
    current_user: CurrentUser
) -> dict[str, Any]:
    """
    Создает новый заказ на основе содержимого корзины пользователя.

    Процесс:
    1. Получение товаров из корзины текущего пользователя.
    2. Расчет итоговой суммы.
    3. Создание записи в таблице заказов.
    4. Очистка корзины.

    Args:
        db: Асинхронная сессия базы данных.
        current_user: Объект текущего авторизованного пользователя.

    Returns:
        Словарь с идентификатором заказа и итоговой суммой.

    Raises:
        HTTPException: Если корзина пользователя пуста.
    """
    query = select(CartItem
                   ).where(CartItem.user_id == current_user.id
                           ).options(selectinload(CartItem.product))
    result = await db.execute(query)
    cart_item = result.scalars().all()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is Empty"
        )
    
    total = sum(item.product.price * item.quantity for item in cart_item)

    new_order = Order(
        user_id=current_user.id,
        total_price=total
    )
    db.add(new_order)

    await db.execute(delete(CartItem).where(CartItem.user_id == current_user.id))
    await db.commit()
    await db.refresh(new_order)

    logger.info("Пользователь {current_user.id} оформил заказ {new_order.id} на сумму {total}")

    return {
        "status": "Order created",
        "order_id": new_order.id,
        "total": total
    }