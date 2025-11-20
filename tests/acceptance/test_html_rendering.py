"""Developer acceptance tests for HTML rendering"""

from fastapi import Request
from fastapi.responses import HTMLResponse

from fastapi_hypermedia import cj_models
from tests.helpers.html_validator import has_html_form, has_html_links


def render_cj_as_html(collection_json):
    """Render Collection+JSON using Jinja2 templates"""
    # Use the Jinja2 environment to render the template properly with inheritance
    import importlib.resources

    from jinja2 import Environment, FileSystemLoader

    templates_dir = importlib.resources.files("fastapi_hypermedia.templates")
    env = Environment(loader=FileSystemLoader(str(templates_dir)))
    template = env.get_template("cj_template.html")
    context = {
        "collection": collection_json.collection,
        "template": collection_json.template,
    }
    return template.render(**context)


def test_developer_can_render_cj_as_html(test_app, test_client, sample_item):
    """As a developer serving both API and web clients, I want to render CJ documents as HTML
    so that browsers get human-readable pages"""

    @test_app.get("/items/{item_id}", response_class=HTMLResponse)
    async def get_item_html(item_id: int):
        cj_item = cj_models.model_to_item(
            sample_item, href=f"http://example.com/items/{sample_item.id}"
        )

        collection = cj_models.Collection(
            href=f"http://example.com/items/{item_id}",
            title="Item Details",
            links=[
                cj_models.Link(rel="self", href=f"http://example.com/items/{item_id}"),
                cj_models.Link(
                    rel="collection",
                    href="http://example.com/items",
                    prompt="Back to Items",
                ),
            ],
            items=[cj_item],
        )
        cj_response = cj_models.CollectionJson(collection=collection)

        html_content = render_cj_as_html(cj_response)
        return HTMLResponse(content=html_content)

    response = test_client.get("/items/1")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    html_content = response.text
    assert has_html_links(html_content)  # Should have navigation links
    assert "Item Details" in html_content
    assert str(sample_item.id) in html_content


def test_developer_can_include_forms_in_html_rendering(test_app, test_client):
    """As a developer, I want CJ templates and queries to render as HTML forms
    so that users can interact with the API through the browser"""

    from fastapi_hypermedia.transitions import TransitionManager
    from tests.conftest import SampleCreateItem

    @test_app.post("/items")
    async def create_item(item: SampleCreateItem):
        pass

    @test_app.get("/items", response_class=HTMLResponse)
    async def get_items_html(request: Request = None):
        tm = TransitionManager(request)
        template = tm.routes_info["create_item"].to_template()

        collection = cj_models.Collection(
            href="http://example.com/items",
            title="Items",
            links=[cj_models.Link(rel="self", href="http://example.com/items")],
        )
        cj_response = cj_models.CollectionJson(
            collection=collection, template=[template]
        )

        html_content = render_cj_as_html(cj_response)
        return HTMLResponse(content=html_content)

    response = test_client.get("/items")
    assert response.status_code == 200

    html_content = response.text
    assert has_html_form(html_content)
    assert 'method="POST"' in html_content  # Should have the template form
    assert 'name="name"' in html_content  # Form fields
    assert 'name="description"' in html_content
