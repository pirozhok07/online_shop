from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Order(Base):
    """
    Модель заказа пользователя.

    Attributes:
        id: Уникальный идентификатор заказа.
        user_id: Идентификатор пользователя (внешний ключ).
        total_price: Общая стоимость заказа.
        status: Текущий статус заказа (по умолчанию "new").
        created_at: Дата и время создания (устанавливается сервером БД).
    """
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    total_price: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(default="new")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, status={self.status}, total={self.total_price})>"