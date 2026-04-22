from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class User(Base):
    """
    Модель пользователя системы.

    Attributes:
        id: Уникальный идентификатор пользователя.
        email: Адрес электронной почты (уникальный, индексируемый).
        hashed_password: Хешированная строка пароля.
        is_active: Статус активности аккаунта (по умолчанию True).
        is_admin: Флаг прав администратора (по умолчанию False).
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_admin: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"<User(email={self.email}, is_admin={self.is_admin})>"
