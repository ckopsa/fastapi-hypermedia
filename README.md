# fastapi-hypermedia

A FastAPI extension for building hypermedia APIs using the Collection+JSON format.

## Features

- **Collection+JSON Support**: Full support for defining responses using the Collection+JSON standard.
- **Hypermedia Transitions**: Dynamically discover and manage links and forms based on your FastAPI routes.
- **HTML Rendering**: Built-in support for rendering Collection+JSON as HTML using Jinja2 templates.

## Installation

Since the package is not yet published to PyPI, you can install it directly from GitHub.

Using pip:

```bash
pip install git+https://github.com/ckopsa/fastapi-hypermedia.git
```

Or using `uv`:

```bash
uv add git+https://github.com/ckopsa/fastapi-hypermedia.git
```

## Usage

Here is a basic example of how to use `fastapi-hypermedia` in your application using the new `Hypermedia` dependency.

```python
from fastapi import FastAPI, Depends, Request
from fastapi_hypermedia import Hypermedia

app = FastAPI()

@app.get("/", name="root")
async def root(request: Request, hm: Hypermedia = Depends(Hypermedia)):
    return hm.create_collection_response(
        title="My API",
        links=["root"]
    )
```

Legacy usage (direct model manipulation) is also supported:

```python
from fastapi import FastAPI, Request
from fastapi_hypermedia import cj_models

app = FastAPI()

@app.get("/legacy")
async def legacy(request: Request):
    collection = cj_models.Collection(
        href=str(request.url),
        title="My API",
        links=[
            cj_models.Link(rel="self", href=str(request.url))
        ]
    )
    return cj_models.CollectionJson(collection=collection)
```

For a complete working example, check the `examples/app` directory.

## Using the Example App as a Starter

The `examples/app` directory contains a complete FastAPI application that you can use as a template for your own projects.

### Getting Started

1.  **Copy the directory**:
    ```bash
    cp -r examples/app my-new-app
    cd my-new-app
    ```

2.  **Install dependencies**:
    The example app uses `uv` for dependency management.
    ```bash
    uv pip install -r requirements.txt
    ```

3.  **Run with Docker Compose**:
    The easiest way to get the application running, including the database, is with Docker Compose.
    ```bash
    docker-compose up --build
    ```
    The app will be available at http://localhost:5000.

4.  **Customize your application**:
    From here, you can start modifying the code in `my-new-app` to fit your needs. You'll likely want to start by updating the models in `models.py`, the database schemas in `db_models/`, and the API routes in `routers/`.

## Development

This project is set up with modern python tooling.

### Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv)

### Getting Started

To start developing, refer to [CONTRIBUTING.md](CONTRIBUTING.md).

Quick start:

```bash
make install
make test
```

## Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) for details on how to submit pull requests.
