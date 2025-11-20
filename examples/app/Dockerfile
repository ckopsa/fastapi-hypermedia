FROM ghcr.io/astral-sh/uv:python3.10-bookworm AS builder

WORKDIR /code
COPY ./pyproject.toml /code/pyproject.toml
COPY ../../../fastapi_hypermedia /code/fastapi_hypermedia
RUN uv sync
CMD ["uv", "run", "fastapi", "run", "main.py", "--proxy-headers", "--port", "80"]