import hashlib
import os
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings

def get_password_hash(
    password: str
) -> str:
    """
    Хеширует пароль с использованием SHA-256 и уникальной соли.

    Args:
        password: Пароль в открытом виде.

    Returns:
        Строка формата 'соль$хеш'.
    """
    salt = os.urandom(32).hex()
    
    hash_obj = hashlib.sha256((password + salt).encode()).hexdigest()

    return f"{salt}${hash_obj}"

def verify_password(
    plain_password: str, 
    hashed_password: str
) -> bool:
    """
    Проверяет пароль, сравнивая его с сохраненным хешем.

    Args:
        plain_password: Пароль, введенный пользователем.
        hashed_password: Хешированная строка из БД (соль$хеш).

    Returns:
        True, если пароли совпадают, иначе False.
    """
    try:
        salt, stored_hash = hashed_password.split("$")
    
        current_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()

        return current_hash == stored_hash
    
    except (ValueError, AttributeError):
        return False

def create_access_token(
    data: dict, 
    expires_delta: timedelta | None = None
) -> str:
    """
    Создает JWT токен доступа.

    Args:
        data: Полезная нагрузка токена (payload).
        expires_delta: Опциональное время истечения.

    Returns:
        Закодированная строка JWT.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
