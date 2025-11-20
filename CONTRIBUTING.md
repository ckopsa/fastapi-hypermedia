# Contributing to fastapi-hypermedia

Thank you for your interest in contributing to `fastapi-hypermedia`! We welcome contributions from the community.

## Development Setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

1.  **Install `uv`**:
    Follow the instructions at [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/) to install `uv`.

2.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-org/fastapi-hypermedia.git
    cd fastapi-hypermedia
    ```

3.  **Install dependencies**:
    ```bash
    make install
    ```
    This will create a virtual environment and install the project in editable mode with development dependencies.

## Running Tests

To run the test suite:

```bash
make test
```

This uses `pytest` to run the tests.

## Linting and Formatting

We use `ruff` for linting and formatting, and `mypy` for type checking.

To check for linting errors and type issues:

```bash
make lint
```

To auto-format the code:

```bash
make format
```

## Running the Example App

There is an example application in `examples/app`. You can run it using:

```bash
make dev
```

This will start the FastAPI server with reloading enabled.

## Pull Request Process

1.  Fork the repository and create your branch from `main`.
2.  Make sure your code passes all linting and tests (`make check`).
3.  Add tests for any new functionality.
4.  Submit a Pull Request!
