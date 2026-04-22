from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class Product(Base):
    """
    Модель товара в каталоге.

    Attributes:
        id: Уникальный идентификатор товара.
        name: Название товара (индексируемое).
        description: Подробное описание товара.
        price: Стоимость товара.
        category: Категория товара (строковое значение).
        rating: Средний рейтинг товара (по умолчанию 0.0).
    """
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(default=None)
    price: Mapped[float] = mapped_column(nullable=False)
    category: Mapped[str | None] = mapped_column(index=True, default=None)
    rating: Mapped[float] = mapped_column(default=0.0)

    def __repr__(self) -> str:
        return f"<Product(name={self.name}, price={self.price})>"