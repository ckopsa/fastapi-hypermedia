"""HTML generation for Collection+JSON documents using dominate"""
from dominate import document
from dominate.tags import *

from . import cj_models


def cj_to_html(cj_data: cj_models.CollectionJson) -> str:
    """Convert Collection+JSON to HTML document"""
    doc = document(title=cj_data.collection.title or 'Collection')

    with doc:
        h1(cj_data.collection.title or 'Collection')

        # Links section
        if cj_data.collection.links:
            h2('Links')
            with ul():
                for link in cj_data.collection.links:
                    li(a(link.prompt or link.rel, href=link.href, rel=link.rel))

        # Items section
        if cj_data.collection.items:
            h2('Items')
            with ul():
                for item in cj_data.collection.items:
                    with li():
                        a(item.href, href=item.href)
                        with ul():
                            for data_item in item.data:
                                li(f"{data_item.prompt or data_item.name}: {data_item.value}")

        # Queries section
        if cj_data.collection.queries:
            h2('Queries')
            for query in cj_data.collection.queries:
                with form(action=query.href, method='GET'):
                    h3(query.prompt or 'Search')
                    for field in query.data:
                        label(field.prompt or field.name)
                        input_(type=field.input_type or 'text', name=field.name,
                             value=field.value, required=field.required)
                        br()
                    button('Search', type='submit')

        # Templates section
        if cj_data.template:
            h2('Create New Item')
            for template in cj_data.template:
                with form(action=template.href, method=template.method or 'POST'):
                    for field in template.data:
                        label(field.prompt or field.name)
                        input_(type=field.input_type or 'text', name=field.name,
                             value=field.value, required=field.required)
                        br()
                    button(template.prompt or 'Submit', type='submit')

    return str(doc)
