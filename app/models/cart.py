from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.product import Product

class CartItem(Base):
    """
    Модель элемента корзины пользователя.

    Attributes:
        id: Уникальный идентификатор записи.
        user_id: ID пользователя, которому принадлежит корзина.
        product_id: ID товара в корзине.
        quantity: Количество товара (по умолчанию 1).
        product: Связанный объект модели Product.
    """
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(default=1)

    product: Mapped["Product"] = relationship("Product")

    def __repr__(self) -> str:
        return f"<CartItem(id={self.id}, status={self.user_id}, total={self.product_id}, quantity={self.quantity})>"