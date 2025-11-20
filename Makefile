.PHONY: install dev lint format test check clean

install:
	uv sync --extra dev

dev:
	cd examples/app && uv run fastapi dev main.py --port 8082

lint:
	uv run ruff check fastapi_hypermedia/
	uv run mypy fastapi_hypermedia/
	uv run ruff check tests/
	uv run mypy examples/app/
	cd examples/app && uv run ruff check .

format:
	uv run ruff check --fix .
	uv run ruff format .

test:
	uv run pytest

check: lint test

clean:
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf coverage
	rm -rf htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
