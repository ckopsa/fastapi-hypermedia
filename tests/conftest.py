import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel


class SampleItem(BaseModel):
    id: int
    name: str
    description: str | None = None
    active: bool = True


class SampleCreateItem(BaseModel):
    name: str
    description: str | None = None


@pytest.fixture
def sample_item():
    """Sample domain model instance"""
    return SampleItem(id=1, name="Test Item", description="A test item", active=True)


@pytest.fixture
def sample_items():
    """List of sample domain models"""
    return [
        SampleItem(id=1, name="Item 1", description="First item", active=True),
        SampleItem(id=2, name="Item 2", description="Second item", active=False),
    ]


from fastapi.routing import APIRoute  # noqa: E402


def generate_unique_id(route: APIRoute) -> str:
    return route.name


@pytest.fixture
def test_app():
    """Minimal FastAPI app for testing"""
    app = FastAPI(
        title="Test Hypermedia API", generate_unique_id_function=generate_unique_id
    )
    return app


@pytest.fixture
def test_client(test_app):
    """TestClient for the test app"""
    return TestClient(test_app)
