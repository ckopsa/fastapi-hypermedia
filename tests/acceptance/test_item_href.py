import importlib.resources

from fastapi import Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

from fastapi_hypermedia import Hypermedia, cj_models
from tests.acceptance.test_html_rendering import render_cj_as_html


def test_item_href_is_visible_in_html(test_app, test_client, sample_item):
    """
    As a user, I want to see a link to the item's detail page on collection pages,
    so I can navigate to individual items.
    """

    @test_app.get("/items", response_class=HTMLResponse)
    async def get_items_html():
        cj_item = cj_models.model_to_item(
            sample_item, href=f"http://testserver/items/{sample_item.id}"
        )

        collection = cj_models.Collection(
            href="http://testserver/items",
            title="Items Collection",
            items=[cj_item],
        )
        cj_response = cj_models.CollectionJson(collection=collection)

        html_content = render_cj_as_html(cj_response)
        return HTMLResponse(content=html_content)

    response = test_client.get("/items")
    assert response.status_code == 200

    html_content = response.text
    assert f'href="http://testserver/items/{sample_item.id}"' in html_content
    assert (
        "hidden" not in html_content
        or f'href="http://testserver/items/{sample_item.id}"'
        not in html_content.split("hidden")[1].split("</h3>")[0]
    )
    assert "Navigate to Instance" in html_content


def test_custom_item_prompt_is_visible_in_html(test_app, test_client, sample_item):
    """
    As a developer, I want to provide a custom label for the item's detail link,
    so I can improve the user experience.
    """

    @test_app.get("/items-custom", response_class=HTMLResponse)
    async def get_items_custom_html():
        cj_item = cj_models.model_to_item(
            sample_item,
            href=f"http://testserver/items/{sample_item.id}",
            prompt="View Details",
        )

        collection = cj_models.Collection(
            href="http://testserver/items-custom",
            title="Items Collection",
            items=[cj_item],
        )
        cj_response = cj_models.CollectionJson(collection=collection)

        html_content = render_cj_as_html(cj_response)
        return HTMLResponse(content=html_content)

    response = test_client.get("/items-custom")
    assert response.status_code == 200

    html_content = response.text
    assert "View Details" in html_content
    assert "Navigate to Instance" not in html_content


def test_hypermedia_helper_with_item_prompt(test_app, test_client, sample_items):
    """
    As a developer using the Hypermedia helper, I want to provide an item_prompt factory
    so that each item in a collection has a dynamic, human-readable label.
    """
    @test_app.get("/items-helper", response_class=HTMLResponse)
    async def get_items_helper(request: Request):
        h = Hypermedia(request)
        return h.create_collection_response(
            title="Helper Collection",
            items=sample_items,
            item_href=lambda x: f"http://testserver/items/{x.id}",
            item_prompt=lambda x: f"Go to {x.name}",
        )

    response = test_client.get("/items-helper")
    assert response.status_code == 200

    html_content = response.text
    assert "Go to Item 1" in html_content
    assert "Go to Item 2" in html_content


def test_item_href_in_future_template(test_app, test_client, sample_item):
    """
    As a user using the 'future' theme, I want to see item hrefs and prompts
    in the HUD and item views.
    """

    @test_app.get("/items-future", response_class=HTMLResponse)
    async def get_items_future():
        cj_item = cj_models.model_to_item(
            sample_item,
            href=f"http://testserver/items/{sample_item.id}",
            prompt="Cyber Link",
        )

        collection = cj_models.Collection(
            href="http://testserver/items-future",
            title="Future Collection",
            items=[cj_item],
        )
        cj_response = cj_models.CollectionJson(collection=collection)

        templates_dir = importlib.resources.files("fastapi_hypermedia.templates")
        env = Environment(loader=FileSystemLoader(str(templates_dir)))
        template = env.get_template("future.html")
        html_content = template.render(
            collection=cj_response.collection, template=cj_response.template
        )

        return HTMLResponse(content=html_content)

    response = test_client.get("/items-future")
    assert response.status_code == 200

    html_content = response.text
    assert "Cyber Link" in html_content
    assert f'href="http://testserver/items/{sample_item.id}"' in html_content
    assert '<i class="fas fa-external-link-alt mr-1"></i> Cyber Link' in html_content
