import datetime
import enum
from collections.abc import Callable
from typing import Any

from fastapi import Request
from fastapi.routing import APIRoute
from pydantic import BaseModel
from pydantic.types import StrictBool

from . import cj_models


class FormProperty(BaseModel):
    """
    Represents a property in a transition form.
    Maps to inputs in HTML forms or data fields in Collection+JSON queries.
    """

    name: str
    type: str
    prompt: str
    value: (
        StrictBool
        | int
        | float
        | dict[str, Any]
        | list[Any]
        | None
        | datetime.datetime
        | datetime.date
        | str
    ) = None
    required: bool = False
    input_type: str | None = None
    options: list[str] | None = None
    render_hint: str | None = None


class Form(BaseModel):
    """
    Represents a transition (link or form) derived from a FastAPI route.
    """

    id: str
    name: str
    href: str
    rel: str
    tags: str
    title: str
    method: str
    properties: list[dict[str, Any]]

    def to_link(self, rel: str | None = None) -> cj_models.Link:
        """Converts the transition to a Collection+JSON Link."""
        return cj_models.Link(
            rel=rel or self.rel,
            href=self.href,
            prompt=self.title,
            method=self.method,
        )

    def to_query(self) -> cj_models.Query:
        """Converts the transition to a Collection+JSON Query."""
        return cj_models.Query(
            rel=self.rel,
            href=self.href,
            prompt=self.title,
            data=[cj_models.TemplateData(**prop) for prop in self.properties],
        )

    def to_template(
        self, defaults: dict[str, str | StrictBool | int | float | None] | None = None
    ) -> cj_models.Template:
        """
        Converts the transition to a Collection+JSON Template.

        Args:
            defaults: A dictionary of default values to populate the template data.
        """
        template_data = []
        for prop in self.properties:
            default_value = defaults.get(prop["name"]) if defaults else None
            if isinstance(default_value, enum.Enum):
                default_value = default_value.value
            if default_value:
                prop["value"] = default_value
            template_data.append(cj_models.TemplateData(**prop))
        return cj_models.Template(
            name=self.name,
            data=template_data,
            prompt=self.title,
            href=self.href,
            method=self.method,
            rel=self.rel,
        )


class TransitionManager:
    """
    Manages hypermedia transitions by dynamically inspecting the FastAPI application's
    OpenAPI schema. It organizes existing routes rather than redefining them.
    """

    def __init__(self, request: Request):
        self.page_transitions: dict[str, list[str]] = {}
        self.item_transitions: dict[str, list[str]] = {}

        if not hasattr(request.app.state, "hypermedia_routes_info"):
            request.app.state.hypermedia_routes_info = {}
            request.app.state.hypermedia_functions_map = {}
            self._load_routes_from_schema(request)

        self.routes_info: dict[str, Form] = request.app.state.hypermedia_routes_info
        self.functions_map: dict[Callable[..., Any], str] = (
            request.app.state.hypermedia_functions_map
        )

    def _load_routes_from_schema(self, request: Request) -> None:
        """
        Parses the OpenAPI schema to build an internal cache of route information.
        """
        # Map functions to operation IDs
        for route in request.app.routes:
            if isinstance(route, APIRoute):
                op_id = route.operation_id
                if not op_id and hasattr(request.app.router, "generate_unique_id_function"):
                    # FastAPI stores generate_unique_id_function in the router
                    op_id = request.app.router.generate_unique_id_function(route)

                if op_id:
                    request.app.state.hypermedia_functions_map[route.endpoint] = op_id

        schema = request.app.openapi()
        for path, path_item in schema.get("paths", {}).items():
            for method, operation in path_item.items():
                op_id = operation.get("operationId")
                if not op_id:
                    continue

                # Extract parameters for form properties
                params: list[FormProperty] = []
                # From path e.g. /wip/{item_id}
                for param in operation.get("parameters", []):
                    if param.get("in") == "path":
                        # params.append(param.get("name"))
                        pass

                # From query parameters
                for param in operation.get("parameters", []):
                    if param.get("in") == "query":
                        params.append(
                            FormProperty(
                                name=param.get("name"),
                                value=param.get("schema", {}).get("default"),
                                type=param.get("schema", {}).get("type", "string"),
                                required=param.get("required", False),
                                prompt=param.get("description", param.get("name")),
                                input_type=param.get("schema", {}).get(
                                    "type", "string"
                                ),
                            )
                        )

                # From request body
                request_body = operation.get("requestBody")
                if request_body:
                    content = request_body.get("content", {})
                    if "application/json" in content:
                        json_schema = content.get("application/json", {}).get(
                            "schema", {}
                        )
                        if json_schema:
                            if "$ref" in json_schema:
                                schema_name = json_schema["$ref"].split("/")[-1]
                                json_schema = (
                                    schema.get("components", {})
                                    .get("schemas", {})
                                    .get(schema_name, {})
                                )
                                for name, props in json_schema.get(
                                    "properties", {}
                                ).items():
                                    # Extract additional schema details
                                    enum_values = props.get("enum")
                                    schema_type = props.get("type", "string")
                                    render_hint = props.get("x-render-hint")

                                    # extract enum values if available
                                    enumRef = props.get("allOf")
                                    if (
                                        enumRef
                                        and isinstance(enumRef, list)
                                        and len(enumRef) > 0
                                    ):
                                        enum_schema_name = (
                                            enumRef[0].get("$ref", "").split("/")[-1]
                                        )
                                        enum_props = (
                                            schema.get("components", {})
                                            .get("schemas", {})
                                            .get(enum_schema_name, {})
                                        )
                                        enum_values = enum_props.get("enum")
                                        schema_type = enum_props.get(
                                            "type", schema_type
                                        )

                                    # Determine input_type
                                    input_type = schema_type  # Default
                                    if schema_type == "boolean":
                                        input_type = "checkbox"
                                    elif (
                                        schema_type == "integer"
                                        or schema_type == "number"
                                    ):
                                        input_type = "number"
                                    elif schema_type == "string" and enum_values:
                                        input_type = "select"
                                    elif schema_type == "string":
                                        input_type = "text"
                                    params.append(
                                        FormProperty(
                                            name=name,
                                            value=props.get("default", None),
                                            type=schema_type,
                                            required=name
                                            in json_schema.get("required", []),
                                            prompt=props.get("title", name),
                                            input_type=input_type,
                                            options=enum_values,
                                            render_hint=render_hint,
                                        )
                                    )
                            else:
                                pass
                    elif "application/x-www-form-urlencoded" in content:
                        form_schema = content.get(
                            "application/x-www-form-urlencoded", {}
                        ).get("schema", {})
                        if form_schema:
                            if "$ref" in form_schema:
                                schema_name = form_schema["$ref"].split("/")[-1]
                                form_schema = (
                                    schema.get("components", {})
                                    .get("schemas", {})
                                    .get(schema_name, {})
                                )
                                for name, props in form_schema.get(
                                    "properties", {}
                                ).items():
                                    # Extract additional schema details
                                    enum_values = props.get("enum")
                                    schema_type = props.get("type", "string")
                                    render_hint = props.get(
                                        "x-render-hint"
                                    )  # Extract render_hint

                                    # Determine input_type
                                    input_type = schema_type  # Default
                                    if schema_type == "boolean":
                                        input_type = "checkbox"
                                    elif (
                                        schema_type == "integer"
                                        or schema_type == "number"
                                    ):
                                        input_type = "number"
                                    elif schema_type == "string" and enum_values:
                                        input_type = "select"
                                    elif schema_type == "string":
                                        input_type = "text"

                                    params.append(
                                        FormProperty(
                                            name=name,
                                            value=props.get("default", None),
                                            type=schema_type,
                                            required=name
                                            in form_schema.get("required", []),
                                            prompt=props.get("title", name),
                                            input_type=input_type,
                                            options=enum_values,
                                            render_hint=render_hint,
                                        )
                                    )
                            else:
                                pass
                request.app.state.hypermedia_routes_info[operation.get("operationId")] = Form(
                    id=operation.get("operationId"),
                    name=operation.get("operationId"),
                    href=path,
                    rel=" ".join(operation.get("tags", []))
                    if operation.get("tags")
                    else "",
                    tags=" ".join(operation.get("tags", [])),
                    title=operation.get("summary", ""),
                    method=method.upper(),
                    properties=[prop.model_dump() for prop in params],
                )

    def get_transition(
        self, transition_name: str | Callable[..., Any], context: dict[str, str]
    ) -> Form | None:
        """
        Retrieves a transition (route) by its operation ID and formats its URL with the provided context.

        Args:
            transition_name: The operation ID of the route, or the endpoint function.
            context: A dictionary of values to format the URL path parameters.

        Returns:
            A Form object representing the transition, or None if not found.
        """
        lookup_name: str | None = None
        if isinstance(transition_name, str):
            lookup_name = transition_name
        else:
            lookup_name = self.functions_map.get(transition_name)

        if not lookup_name:
            return None

        form = self.routes_info.get(lookup_name)
        if form is not None:
            form = form.model_copy(deep=True)
            try:
                form.href = form.href.format(**context)
            except KeyError as e:
                raise KeyError(
                    f"Missing parameter {e} for route '{transition_name}' with href '{form.href}'"
                ) from e
        return form
