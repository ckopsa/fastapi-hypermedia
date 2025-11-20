# fastapi-hypermedia

A FastAPI extension for building hypermedia APIs using the Collection+JSON format.

## Installation

Install the core package:

```bash
pip install fastapi-hypermedia
```

For development with the example app (optional):

```bash
pip install fastapi-hypermedia[app]
```

## Usage

Import and use the hypermedia components in your FastAPI app:

```python
from fastapi_hypermedia import cj_models, transitions
# ... build hypermedia responses
```

## Example App

An example FastAPI application demonstrating hypermedia functionality is provided in `examples/app/`.

To run the example:

```bash
cd examples/app
pip install -r requirements.txt
uvicorn main:app --reload
```

## Features

- Collection+JSON model definitions
- Hypermedia transitions
- Programmatic HTML generation using dominate
- Templating support for HTML rendering (alternative)
