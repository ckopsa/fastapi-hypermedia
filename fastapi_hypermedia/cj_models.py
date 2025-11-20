from __future__ import annotations

import datetime

from pydantic import BaseModel
from pydantic import Field as PydanticField
from pydantic.types import StrictBool


class Link(BaseModel):
    rel: str
    href: str
    prompt: str | None = None
    render: str | None = None
    media_type: str | None = None
    method: str | None = PydanticField("GET", description="HTTP method for the link")


class ItemData(BaseModel):
    name: str
    value: (
        StrictBool
        | int
        | float
        | dict
        | list
        | None
        | datetime.datetime
        | datetime.date
        | str
    ) = PydanticField(None, description="Value of the data item")
    prompt: str | None = PydanticField(
        None, description="Human Readable prompt for the data"
    )
    type: str | None = PydanticField(None, description="Type of the data")
    input_type: str | None = PydanticField(
        None,
        description="Suggested input type (e.g., 'text', 'checkbox', 'number', 'select')",
    )
    render_hint: str | None = PydanticField(
        None,
        description="A hint for how to render the data item (e.g., 'textarea', 'colorpicker')",
    )


class QueryData(ItemData):
    options: list[str] | None = PydanticField(
        None, description="List of options for 'select' input type"
    )


class TemplateData(QueryData):
    required: bool | None = False


class Query(BaseModel):
    rel: str
    href: str
    prompt: str | None = None
    name: str | None = None
    data: list[QueryData] = PydanticField(default_factory=list)


class Item(BaseModel):
    href: str
    rel: str
    data: list[ItemData] = PydanticField(default_factory=list)
    links: list[Link] = PydanticField(default_factory=list)


class Collection(BaseModel):
    version: str = "1.0"
    href: str
    title: str
    links: list[Link] = PydanticField(default_factory=list)
    items: list[Item] = PydanticField(default_factory=list)
    queries: list[Query] = PydanticField(default_factory=list)


class Template(BaseModel):
    name: str
    data: list[TemplateData] = PydanticField(default_factory=list)
    href: str | None = None
    method: str | None = PydanticField(
        "POST", description="HTTP method for the template"
    )
    prompt: str | None = None
    rel: str | None = None


class Error(BaseModel):
    title: str
    code: int
    message: str
    details: str | None = None


class CollectionJson(BaseModel):
    collection: Collection
    template: list[Template] | None = PydanticField(
        None, description="Templates for the collection"
    )
    error: Error | None = PydanticField(None, description="Error details, if any")


def to_collection_json_data(self: BaseModel, href="", links=None, rel="item") -> Item:
    """
    Converts a Pydantic model instance into a Collection+JSON 'data' array.
    'self' will be the model instance when this is called.
    """
    schema = self.model_json_schema()
    model_dict = self.model_dump()
    cj_data = []

    for name, definition in schema.get("properties", {}).items():
        cj_data.append(
            ItemData(
                name=name,
                value=model_dict.get(name),
                prompt=definition.get("title") or name.replace("_", " ").title(),
                type=definition.get("type"),
                render_hint=definition.get("x-render-hint"),
            )
        )
    return Item(
        href=href,
        rel=rel,
        data=cj_data,
        links=links or [],
    )


BaseModel.to_cj_data = to_collection_json_data
