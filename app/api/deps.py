from typing import Annotated

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import oauth2_scheme
from app.core.config import settings 
from app.database import get_db
from app.models import User


# Псевдонимы типов
DBSession = Annotated[AsyncSession, Depends(get_db)]
Token = Annotated[str, Depends(oauth2_scheme)]

async def get_current_user(
    token: Token, db: DBSession
) -> User:
    """
    Проверяет валидность JWT-токена и возвращает текущего пользователя.

    Args:
        token: JWT-токен из заголовка Authorization.
        db: Асинхронная сессия базы данных.

    Returns:
        Объект пользователя User.

    Raises:
        HTTPException: Ошибка 401, если токен невалиден или пользователь не найден.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalars().first()

    if user is None:
        raise credentials_exception
    
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

async def get_current_admin(
    current_user: CurrentUser
) -> User:
    """
    Проверяет, является ли текущий пользователь администратором.

    Args:
        current_user: Текущий авторизованный пользователь.

    Returns:
        Объект пользователя с правами администратора.

    Raises:
        HTTPException: Ошибка 403, если у пользователя нет прав администратора.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции"
        )
    
    return current_user