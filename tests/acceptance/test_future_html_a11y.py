import importlib.resources

from jinja2 import Environment, FileSystemLoader

from fastapi_hypermedia import cj_models


def render_future_as_html(collection_json):
    """Render Collection+JSON using the 'future.html' template"""
    templates_dir = importlib.resources.files("fastapi_hypermedia.templates")
    env = Environment(loader=FileSystemLoader(str(templates_dir)))
    template = env.get_template("future.html")
    context = {
        "collection": collection_json.collection,
        "template": collection_json.template,
    }
    return template.render(**context)


def test_future_html_accessibility():
    """Verify that 'future.html' has critical accessibility attributes and structure"""

    # Create dummy data for rendering
    collection = cj_models.Collection(
        href="http://example.com/items",
        title="Items",
        links=[cj_models.Link(rel="self", href="http://example.com/items")],
        items=[
            cj_models.Item(
                href="http://example.com/items/1",
                rel="item",
                data=[cj_models.ItemData(name="title", value="Test Item 1")],
            )
        ],
    )
    cj_response = cj_models.CollectionJson(collection=collection)

    html_content = render_future_as_html(cj_response)

    # Assertions for expected accessibility attributes

    # 1. Dialog Role
    assert 'role="dialog"' in html_content
    assert 'aria-modal="true"' in html_content
    assert 'aria-label="Command Palette"' in html_content

    # 2. Input Accessibility
    assert 'role="combobox"' in html_content
    assert 'aria-autocomplete="list"' in html_content
    assert 'aria-expanded="true"' in html_content
    assert 'aria-controls="hud-list"' in html_content
    assert 'aria-label="Filter commands and items"' in html_content

    # 3. List Structure
    assert 'role="listbox"' in html_content
    assert 'role="group"' in html_content

    # 4. Hidden Icons
    # Check that icons have aria-hidden="true"
    assert (
        'class="fas fa-terminal text-pink-500 mr-3" aria-hidden="true"' in html_content
        or 'aria-hidden="true"' in html_content
    )

    # 5. List Items and IDs
    assert 'role="option"' in html_content
    assert 'aria-selected="false"' in html_content

    # Verify IDs are generated (e.g., hud-opt-item-1)
    assert 'id="hud-opt-item-1"' in html_content

    # Verify close button a11y
    assert 'aria-label="Close item details"' in html_content
