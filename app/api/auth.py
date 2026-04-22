from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.core.security import get_password_hash, verify_password, create_access_token
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut

# Настройка схемы аутентификации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Псевдонимы типов
DBSession = Annotated[AsyncSession, Depends(get_db)]
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
Token = Annotated[str, Depends(oauth2_scheme)]

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    summary="Вход в систему",
    response_description="JWT токен доступа"
)
async def login(
    form_data: OAuth2Form, 
    db: DBSession
) -> dict[str, str]:
    """
    Проверяет учетные данные пользователя и возвращает JWT токен.
    Args:
        form_data: Данные формы аутентификации (username/password).
        db: Сессия асинхронного подключения к базе данных.

    Returns:
        Словарь с токеном доступа и его типом.

    Raises:
        HTTPException: Ошибка 401 при неверном логине или пароле.
    """
    query = select(User).where(User.email == form_data.username)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Неудачная попытка входа: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
            )

    access_token = create_access_token(data={"sub": user.email})
    logger.info(f"Пользователь {user.email} успешно авторизован")

    return {"access_token": access_token, "token_type": "bearer"}

@router.post(
    "/register", 
    response_model=UserOut, 
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация"
)
async def register(
    user_data: UserCreate, 
    db: DBSession
) -> User:
    """
    Регистрирует нового пользователя.

    Args:
        user_data: Схема данных нового пользователя.
        db: Сессия базы данных.

    Returns:
        Созданный объект пользователя.
    """
    query = select(User).where(User.email == user_data.email)
    result = await db.execute(query)
    if result.scalars().first():
        logger.error(f"Пользователь {user_data.email} уже зарегистрирован")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
            )
    
    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(email=user_data.email, hashed_password=hashed_pwd)
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.info(f"Зарегистрирован новый пользователь: {new_user.email}")
    return new_user
