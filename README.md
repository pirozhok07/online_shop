# 🛒 Async Online Store API (FastAPI)

Полноценный бэкенд для интернет-магазина с асинхронной архитектурой, JWT-авторизацией и корзиной.

## 🛠 Технологический стек
- **Framework:** FastAPI (Python 3.10+)
- **Database:** SQLite + SQLAlchemy 2.0 (Async engine)
- **Migrations:** Alembic
- **Testing:** Pytest + HTTPX (In-memory DB)
- **Security:** JWT (Python-Jose) + Salted Password Hashing (Hashlib)
- **Validation:** Pydantic v2

## 🚀 Ключевые фичи
- **Async/Await:** Полностью асинхронный пайплайн обработки запросов к БД.
- **JWT Auth:** Безопасная авторизация. Пароли хранятся в виде соли и хеша (SHA-256).
- **Advanced Filtering:** Динамические SQL-запросы для поиска товаров по цене и категориям.
- **Smart Cart:** Реализация связи Many-to-Many с защитой данных (пользователь видит только свою корзину).
- **Reliability:** Покрытие критической логики интеграционными тестами.

## 📦 Как запустить проект
1. Клонируйте репозиторий: `git clone <link>`
2. Установите зависимости: `pip install -r requirements.txt`
3. Примените миграции: `alembic upgrade head`
4. Запустите сервер: `uvicorn app.main:app --reload`
5. Документация доступна по адресу: `http://127.0.0.1:8000/docs`

## 🧪 Тестирование
Запуск тестов в изолированной базе данных:
```bash
python -m pytest
