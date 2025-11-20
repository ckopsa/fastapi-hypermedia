from fastapi import Depends, Request
from pydantic import BaseModel

from fastapi_hypermedia import Hypermedia


def test_improved_dx_usage(test_app, test_client):
    class Item(BaseModel):
        id: int
        name: str

    @test_app.get("/items", name="list_items", tags=["items"])
    async def list_items(request: Request, hm: Hypermedia = Depends(Hypermedia)):
        items = [Item(id=1, name="Item 1"), Item(id=2, name="Item 2")]

        return hm.create_collection_response(
            title="Items",
            items=items,
            item_href=lambda item: f"/items/{item.id}",
            links=[("list_items", "self")],
        )

    response = test_client.get("/items")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.collection+json"

    data = response.json()
    assert data["collection"]["title"] == "Items"
    assert len(data["collection"]["items"]) == 2
    assert data["collection"]["items"][0]["href"] == "/items/1"
    assert data["collection"]["items"][0]["data"][0]["name"] == "id"
    assert data["collection"]["items"][0]["data"][0]["value"] == 1

    assert len(data["collection"]["links"]) == 1
    assert data["collection"]["links"][0]["rel"] == "self"
    assert data["collection"]["links"][0]["href"] == "/items"


def test_queries_and_templates_dx(test_app, test_client):
    @test_app.get("/search", name="search_items", tags=["search"])
    async def search_items(
        q: str, request: Request, hm: Hypermedia = Depends(Hypermedia)
    ):
        return hm.create_collection_response(
            title="Search Results", queries=[("search_items", "search")]
        )

    @test_app.post("/items", name="create_item", tags=["items"])
    async def create_item(
        item: dict, request: Request, hm: Hypermedia = Depends(Hypermedia)
    ):
        return {}

    @test_app.get("/root", name="root")
    async def root(request: Request, hm: Hypermedia = Depends(Hypermedia)):
        return hm.create_collection_response(
            title="Root", templates=[("create_item", "create")]
        )

    # Test Query
    response = test_client.get("/search?q=test")
    data = response.json()
    assert len(data["collection"]["queries"]) == 1
    assert data["collection"]["queries"][0]["rel"] == "search"
    assert data["collection"]["queries"][0]["href"] == "/search"
    assert data["collection"]["queries"][0]["data"][0]["name"] == "q"

    # Test Template
    response = test_client.get("/root")
    data = response.json()
    assert len(data["template"]) == 1
    assert data["template"][0]["rel"] == "create"
    assert data["template"][0]["href"] == "/items"


def test_string_references(test_app, test_client):
    @test_app.get("/simple", name="simple_link", tags=["simple"])
    async def simple_link(request: Request, hm: Hypermedia = Depends(Hypermedia)):
        return hm.create_collection_response(
            title="Simple",
            links=["simple_link"],
            queries=["simple_link"],
            templates=["simple_link"],
        )

    response = test_client.get("/simple")
    data = response.json()

    assert len(data["collection"]["links"]) == 1
    assert data["collection"]["links"][0]["rel"] == "simple"  # from tag

    assert len(data["collection"]["queries"]) == 1
    assert data["collection"]["queries"][0]["rel"] == "simple"

    assert len(data["template"]) == 1
    assert data["template"][0]["rel"] == "simple"
