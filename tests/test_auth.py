import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_register_user(client)-> None:
    """
    Тестирует успешную регистрацию нового пользователя.
    
    Проверяет:
    1. Статус ответа 201 (Created).
    2. Соответствие email в ответе.
    3. Наличие id созданного пользователя.
    """
    response = await client.post(
        "/auth/register",
        json={"email": "test@test.com", "password": "testpassword"}
    )

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["email"] == "test@test.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_login_user(client) -> None:
    """
    Тестирует успешный вход пользователя и получение JWT-токена.
    
    Проверяет:
    1. Возможность логина сразу после регистрации.
    2. Статус ответа 200 (OK).
    3. Наличие access_token и типа токена в ответе.
    """
    await client.post(
        "/auth/register",
        json={"email": "login@test.com", "password": "loginpassword"}
    )
    response = await client.post(
        "/auth/login",
        data={"username": "login@test.com", "password": "loginpassword"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    """
    Тестирует отказ в доступе при неверном пароле.
    """
    await client.post(
        "/auth/register", 
        json={"email": "wrong@test.com", "password": "password123"}
    )

    response = await client.post(
        "/auth/login", 
        data={"username": "wrong@test.com", "password": "wrong_password"}
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect email or password"