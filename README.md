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
    # Simple collection with automatic item HREF and prompt generation
    items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
    return hm.create_collection_response(
        title="My API",
        items=items,
        item_href=lambda x: str(request.url_for("get_item", item_id=x["id"])),
        item_prompt=lambda x: f"View {x['name']}",
        links=["root"]
    )

@app.get("/items/{item_id}", name="get_item")
async def get_item(item_id: int):
    return {"id": item_id, "name": f"Item {item_id}"}
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
