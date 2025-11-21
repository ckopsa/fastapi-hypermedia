import pytest
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


def test_parameterized_links_and_functions(test_app, test_client):
    @test_app.get("/items/{item_id}", name="read_item")
    def read_item(item_id: int):
        return {"item_id": item_id}

    @test_app.get("/users/{user_id}/posts/{post_id}", name="read_post")
    def read_post(user_id: int, post_id: int):
        return {"user_id": user_id, "post_id": post_id}

    @test_app.get("/", name="root")
    def root(request: Request, hm: Hypermedia = Depends(Hypermedia)):
        return hm.create_collection_response(
            title="Test API",
            links=[
                "root",
                ("read_item", {"item_id": 1}),
                (read_item, {"item_id": 2}),
                (read_post, "my_post", {"user_id": 10, "post_id": 20}),
            ],
        )

    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    links = data["collection"]["links"]

    def find_link(href_part):
        return next((link for link in links if href_part in link["href"]), None)

    # 2. ("read_item", {"item_id": 1}) -> href: .../items/1
    link_item_1 = find_link("/items/1")
    assert link_item_1 is not None

    # 3. (read_item, {"item_id": 2}) -> href: .../items/2
    link_item_2 = find_link("/items/2")
    assert link_item_2 is not None

    # 4. (read_post, "my_post", {"user_id": 10, "post_id": 20})
    link_post = find_link("/users/10/posts/20")
    assert link_post is not None
    assert link_post["rel"] == "my_post"


def test_missing_params_error(test_app, test_client):
    @test_app.get("/items/{item_id}", name="read_item")
    def read_item(item_id: int):
        return {"item_id": item_id}

    @test_app.get("/fail")
    def fail_endpoint(hm: Hypermedia = Depends(Hypermedia)):
        return hm.create_collection_response(
            title="Fail",
            links=[read_item],  # Missing item_id
        )

    with pytest.raises(KeyError) as excinfo:
        test_client.get("/fail")

    assert "Missing parameter" in str(excinfo.value)
    assert "item_id" in str(excinfo.value)


def test_linkdef_usage(test_app, test_client):
    from fastapi_hypermedia import LinkDef

    @test_app.get("/linkdef", name="linkdef_route")
    async def linkdef_route(request: Request, hm: Hypermedia = Depends(Hypermedia)):
        return hm.create_collection_response(
            title="LinkDef Test",
            links=[
                LinkDef(name="linkdef_route", rel="self"),
                LinkDef(name="linkdef_route", rel="other", params={"q": "test"}),
            ],
        )

    response = test_client.get("/linkdef")
    data = response.json()
    assert len(data["collection"]["links"]) == 2
    assert data["collection"]["links"][0]["rel"] == "self"
    assert data["collection"]["links"][1]["rel"] == "other"
