install:
	pip install -r requirements.txt

migrate:
	alembic upgrade head

test:
	python -m pytest -v

run:
	uvicorn app.main:app --reload
