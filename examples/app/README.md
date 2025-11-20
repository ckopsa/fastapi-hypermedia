# Example App

This is an example FastAPI application demonstrating the `fastapi-hypermedia` package.

## Running with Docker Compose

```bash
docker-compose up --build
```

The app will be available at http://localhost:5000

## Configuration

- `USE_DOMINATE=true`: Use dominate for HTML generation (default)
- `USE_DOMINATE=false`: Use Jinja2 templates instead

Set via environment variables or modify `.env` file.

## Features

- Collection+JSON API endpoints
- HTML rendering using either dominate or templates
- Authentication and authorization
- Workflow management examples
