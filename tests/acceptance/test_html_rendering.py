from bs4 import BeautifulSoup
from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.testclient import TestClient

from fastapi_hypermedia import Hypermedia, cj_models
from fastapi_hypermedia.templating import get_templates
from tests.helpers.html_validator import has_html_form, has_html_links

"""Developer acceptance tests for HTML rendering"""


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


app = FastAPI()

templates = get_templates()


@app.post("/submit", name="submit_form", operation_id="submit_form")
async def submit_form(
    name: str = Form(...),
    email: str = Form(...),
    optional_field: str | None = Form(None),
):
    return {"message": "Success"}


@app.get("/", name="root", operation_id="root", response_class=HTMLResponse)
async def root(request: Request, hm: Hypermedia = Depends(Hypermedia)):
    cj = hm.create_collection_json(
        title="Required Field Test",
        templates=["submit_form"],
    )
    return templates.TemplateResponse(
        "cj_template.html",
        {"request": request, "collection": cj.collection, "template": cj.template},
    )


client = TestClient(app)


def test_required_fields_rendering():
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    # Check 'name' field
    name_label = soup.find("label", attrs={"for": "template_page_1_name"})
    assert name_label is not None
    assert "*" in name_label.text

    name_input = soup.find("input", attrs={"name": "name"})
    assert name_input is not None
    assert name_input.has_attr("required")
    assert name_input["aria-required"] == "true"

    # Check 'email' field
    email_label = soup.find("label", attrs={"for": "template_page_2_email"})
    assert email_label is not None
    assert "*" in email_label.text

    email_input = soup.find("input", attrs={"name": "email"})
    assert email_input is not None
    assert email_input.has_attr("required")
    assert email_input["aria-required"] == "true"

    # Check 'optional_field' field
    optional_label = soup.find("label", attrs={"for": "template_page_3_optional_field"})
    assert optional_label is not None
    assert "*" not in optional_label.text

    optional_input = soup.find("input", attrs={"name": "optional_field"})
    assert optional_input is not None
    assert not optional_input.has_attr("required")
    assert not optional_input.has_attr("aria-required")
