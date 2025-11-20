"""Developer acceptance tests for hypermedia API scenarios"""

from fastapi import Request
from fastapi.responses import JSONResponse

from fastapi_hypermedia import cj_models
from tests.helpers.cj_validator import is_valid_collection_json_response


def test_developer_can_return_collection_json_response(
    test_app, test_client, sample_items
):
    """As a developer building a hypermedia API, I want to return a valid Collection+JSON document
    so that clients can navigate the API"""

    @test_app.get("/items")
    async def get_items():
        collection = cj_models.Collection(
            href="http://example.com/items",
            title="Items Collection",
            links=[],
            items=[
                cj_models.model_to_item(
                    item, href=f"http://example.com/items/{item.id}"
                )
                for item in sample_items
            ],
        )
        cj_response = cj_models.CollectionJson(collection=collection)
        return JSONResponse(
            content=cj_response.model_dump(),
            media_type="application/vnd.collection+json",
        )

    response = test_client.get("/items")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.collection+json"

    data = response.json()
    assert is_valid_collection_json_response(data)
    assert data["collection"]["title"] == "Items Collection"
    assert len(data["collection"]["items"]) == 2
    assert data["collection"]["items"][0]["data"][0]["name"] == "id"


def test_developer_can_include_links_in_collection(test_app, test_client):
    """As a developer, I want to add navigation links to my collection responses
    so that clients can discover related resources"""

    @test_app.get("/items")
    async def get_items():
        collection = cj_models.Collection(
            href="http://example.com/items",
            title="Items Collection",
            links=[
                cj_models.Link(rel="self", href="http://example.com/items"),
                cj_models.Link(
                    rel="create",
                    href="http://example.com/items",
                    method="POST",
                    prompt="Create Item",
                ),
            ],
            items=[],
        )
        cj_response = cj_models.CollectionJson(collection=collection)
        return JSONResponse(
            content=cj_response.model_dump(),
            media_type="application/vnd.collection+json",
        )

    response = test_client.get("/items")
    assert response.status_code == 200

    data = response.json()
    assert is_valid_collection_json_response(data)
    assert len(data["collection"]["links"]) == 2
    assert data["collection"]["links"][0]["rel"] == "self"
    assert data["collection"]["links"][1]["rel"] == "create"
    assert data["collection"]["links"][1]["method"] == "POST"


def test_developer_can_convert_domain_models_to_cj_items(
    test_app, test_client, sample_item
):
    """As a developer with Pydantic domain models, I want to automatically convert them to CJ item data
    so that I don't manually map fields"""

    @test_app.get("/items/{item_id}")
    async def get_item(item_id: int):
        # Simulate fetching item
        item = sample_item

        cj_item = cj_models.model_to_item(
            item, href=f"http://example.com/items/{item.id}"
        )
        collection = cj_models.Collection(
            href=f"http://example.com/items/{item_id}",
            title="Single Item",
            items=[cj_item],
        )
        cj_response = cj_models.CollectionJson(collection=collection)
        return JSONResponse(
            content=cj_response.model_dump(),
            media_type="application/vnd.collection+json",
        )

    response = test_client.get("/items/1")
    assert response.status_code == 200

    data = response.json()
    assert is_valid_collection_json_response(data)
    item_data = data["collection"]["items"][0]["data"]

    # Verify fields were converted correctly
    field_names = [field["name"] for field in item_data]
    assert "id" in field_names
    assert "name" in field_names
    assert "description" in field_names
    assert "active" in field_names

    # Verify values
    id_field = next(f for f in item_data if f["name"] == "id")
    assert id_field["value"] == 1
    name_field = next(f for f in item_data if f["name"] == "name")
    assert name_field["value"] == "Test Item"


def test_developer_can_generate_queries_from_routes(test_app, test_client):
    """As a developer defining FastAPI routes with query parameters, I want the transition manager
    to generate CJ queries so that clients know how to search/filter"""

    from fastapi_hypermedia.transitions import TransitionManager

    @test_app.get("/items")
    async def get_items(search: str = None, limit: int = 10, request: Request = None):
        # This route has query params that should be discoverable
        tm = TransitionManager(request)
        # Get the query for this route
        query = tm.routes_info["get_items"].to_query()
        # Return it in the collection
        collection = cj_models.Collection(
            href="http://example.com/items", title="Items", queries=[query]
        )
        return cj_models.CollectionJson(collection=collection)

    response = test_client.get("/items")
    assert response.status_code == 200

    data = response.json()
    assert is_valid_collection_json_response(data)
    assert len(data["collection"]["queries"]) == 1

    query = data["collection"]["queries"][0]
    assert query["rel"] == ""  # From tags
    assert query["href"] == "/items"

    # Check that query parameters are included
    query_data_names = [qd["name"] for qd in query["data"]]
    assert "search" in query_data_names
    assert "limit" in query_data_names


def test_developer_can_generate_templates_from_routes(test_app, test_client):
    """As a developer defining POST/PUT routes, I want the transition manager to generate CJ templates
    so that clients know how to submit data"""

    from fastapi_hypermedia.transitions import TransitionManager
    from tests.conftest import SampleCreateItem

    @test_app.post("/items")
    async def create_item(item: SampleCreateItem, request: Request = None):
        # This would normally create the item
        pass

    @test_app.get("/items")
    async def get_items(request: Request = None):
        tm = TransitionManager(request)
        template = tm.routes_info["create_item"].to_template()

        collection = cj_models.Collection(
            href="http://example.com/items", title="Items"
        )
        return cj_models.CollectionJson(collection=collection, template=[template])

    response = test_client.get("/items")
    assert response.status_code == 200

    data = response.json()
    assert is_valid_collection_json_response(data)
    assert len(data["template"]) == 1

    template = data["template"][0]
    assert template["name"] == "create_item"
    assert template["method"] == "POST"
    assert template["href"] == "/items"

    # Check template data fields
    template_data_names = [td["name"] for td in template["data"]]
    assert "name" in template_data_names
    assert "description" in template_data_names
