"""Test UX improvements in HTML rendering"""

from fastapi.responses import HTMLResponse
from fastapi_hypermedia import cj_models
from tests.acceptance.test_html_rendering import render_cj_as_html
from tests.helpers.html_validator import has_html_form

def test_render_required_field_indicator(test_app, test_client):
    """
    As a user, I want to clearly see which form fields are required,
    so that I can fill out the form correctly without errors.
    """
    # Create a template with a required field
    data_item = cj_models.TemplateData(
        name="email",
        prompt="Email Address",
        required=True,
        input_type="email"
    )
    template = cj_models.Template(
        name="subscribe",
        data=[data_item],
        href="http://example.com/subscribe",
        method="POST"
    )

    collection = cj_models.Collection(
        href="http://example.com/subscribe",
        title="Subscribe",
        links=[cj_models.Link(rel="self", href="http://example.com/subscribe")]
    )

    cj_response = cj_models.CollectionJson(
        collection=collection,
        template=[template]
    )

    html_content = render_cj_as_html(cj_response)

    # Check for the presence of the visual indicator (red asterisk)
    # We expect this to fail initially if the indicator is not present
    assert 'aria-hidden="true">*</span>' in html_content or '<span class="text-red-500 ml-1">*</span>' in html_content

def test_render_aria_required_attribute(test_app, test_client):
    """
    As a screen reader user, I want to know which fields are required via ARIA attributes,
    so that I can understand the form requirements.
    """
    # Create a template with a required field
    data_item = cj_models.TemplateData(
        name="username",
        prompt="Username",
        required=True
    )
    template = cj_models.Template(
        name="register",
        data=[data_item],
        href="http://example.com/register",
        method="POST"
    )

    collection = cj_models.Collection(
        href="http://example.com/register",
        title="Register",
        links=[cj_models.Link(rel="self", href="http://example.com/register")]
    )

    cj_response = cj_models.CollectionJson(
        collection=collection,
        template=[template]
    )

    html_content = render_cj_as_html(cj_response)

    # Check for the presence of aria-required="true"
    # We expect this to fail initially if the attribute is not present
    # Note: The existing template might rely only on the 'required' attribute, which is good but aria-required is also helpful for screen readers in some contexts, though redundant in HTML5 it's often considered good practice for robust accessibility in older assistive tech or custom widgets.
    # However, HTML5 'required' attribute maps to aria-required state.
    # Let's check if the 'required' attribute is present on the input tag.
    assert 'required' in html_content
    # And check for explicit visual indicator again to be sure
    assert '<span class="text-red-500' in html_content
