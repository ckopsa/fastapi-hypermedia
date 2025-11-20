"""Developer acceptance tests for transition discovery"""

from fastapi_hypermedia.transitions import TransitionManager
from tests.conftest import SampleCreateItem


def test_developer_can_discover_available_transitions(test_app):
    """As a developer, I want to automatically discover all possible state transitions from my FastAPI app
    so that I can build comprehensive hypermedia controls"""

    @test_app.get("/items")
    async def get_items():
        pass

    @test_app.post("/items")
    async def create_item(item: SampleCreateItem):
        pass

    @test_app.get("/items/{item_id}")
    async def get_item(item_id: int):
        pass

    @test_app.put("/items/{item_id}")
    async def update_item(item_id: int, item: SampleCreateItem):
        pass

    @test_app.delete("/items/{item_id}")
    async def delete_item(item_id: int):
        pass

    # Create a mock request for the transition manager
    class MockRequest:
        def __init__(self, app):
            self.app = app

    request = MockRequest(test_app)
    tm = TransitionManager(request)

    # Verify that transitions were discovered
    assert len(tm.routes_info) > 0

    # Check specific routes
    assert "get_items" in tm.routes_info
    assert "create_item" in tm.routes_info
    assert "get_item" in tm.routes_info
    assert "update_item" in tm.routes_info
    assert "delete_item" in tm.routes_info

    # Verify route details
    get_items_form = tm.routes_info["get_items"]
    assert get_items_form.method == "GET"
    assert get_items_form.href == "/items"

    create_item_form = tm.routes_info["create_item"]
    assert create_item_form.method == "POST"
    assert create_item_form.href == "/items"
    assert len(create_item_form.properties) == 2  # name and description

    update_item_form = tm.routes_info["update_item"]
    assert update_item_form.method == "PUT"
    assert update_item_form.href == "/items/{item_id}"
