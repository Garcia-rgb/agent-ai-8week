.PHONY: install run test lint seed docker-up

install:
	python -m pip install -e ".[dev]"

run:
	uvicorn support_agent.main:app --reload

test:
	pytest -q

lint:
	ruff check --no-cache .

seed:
	python scripts/seed.py

docker-up:
	docker compose up --build
