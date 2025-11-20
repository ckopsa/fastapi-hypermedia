from collections.abc import Callable, Sequence
from typing import Any

from fastapi import Request
from pydantic import BaseModel

from .cj_models import Collection, CollectionJson, Item, Link, Query, Template
from .responses import CollectionResponse
from .transitions import TransitionManager


class Hypermedia:
    """
    A helper class to simplify the creation of Hypermedia responses.
    """

    def __init__(self, request: Request):
        self.request = request
        self.tm = TransitionManager(request)

    def create_collection_response(
        self,
        title: str,
        href: str | None = None,
        items: Sequence[BaseModel | Item | Any] | None = None,
        item_href: Callable[[Any], str] | None = None,
        links: Sequence[str | Link | tuple[Any, ...] | Callable[..., Any]]
        | None = None,
        queries: Sequence[str | Query | tuple[Any, ...] | Callable[..., Any]]
        | None = None,
        templates: Sequence[str | Template | tuple[Any, ...] | Callable[..., Any]]
        | None = None,
        error: Any = None,
    ) -> CollectionResponse:
        """
        Creates a CollectionResponse with the given data.

        Args:
            title: The title of the collection.
            href: The URI of the collection (default: current request URL).
            items: A list of items (Pydantic models, Items, or objects with to_cj_data).
            item_href: A function to generate the HREF for an item.
            links: A list of links (Link objects, route names, or (route_name, rel) tuples).
            queries: A list of queries (Query objects, route names, or (route_name, rel) tuples).
            templates: A list of templates (Template objects, route names, or (route_name, rel) tuples).
            error: An optional error object.

        Returns:
            A CollectionResponse.
        """
        cj = self.create_collection_json(
            title=title,
            href=href,
            items=items,
            item_href=item_href,
            links=links,
            queries=queries,
            templates=templates,
            error=error,
        )
        return CollectionResponse(cj)

    def create_collection_json(
        self,
        title: str,
        href: str | None = None,
        items: Sequence[BaseModel | Item | Any] | None = None,
        item_href: Callable[[Any], str] | None = None,
        links: Sequence[str | Link | tuple[Any, ...] | Callable[..., Any]] | None = None,
        queries: Sequence[str | Query | tuple[Any, ...] | Callable[..., Any]] | None = None,
        templates: Sequence[str | Template | tuple[Any, ...] | Callable[..., Any]] | None = None,
        error: Any = None,
    ) -> CollectionJson:
        """
        Creates a CollectionJson object with the given data.

        Args:
            title: The title of the collection.
            href: The URI of the collection (default: current request URL).
            items: A list of items (Pydantic models, Items, or objects with to_cj_data).
            item_href: A function to generate the HREF for an item.
            links: A list of links (Link objects, route names, or (route_name, rel) tuples).
            queries: A list of queries (Query objects, route names, or (route_name, rel) tuples).
            templates: A list of templates (Template objects, route names, or (route_name, rel) tuples).
            error: An optional error object.

        Returns:
            A CollectionJson object.
        """
        href = href or str(self.request.url)
        items = items or []
        links = links or []
        queries = queries or []
        templates = templates or []

        cj_items = self._process_items(items, item_href)
        cj_links = self._process_links(links)
        cj_queries = self._process_queries(queries)
        cj_templates = self._process_templates(templates)

        collection = Collection(
            href=href,
            title=title,
            items=cj_items,
            links=cj_links,
            queries=cj_queries,
        )

        return CollectionJson(
            collection=collection,
            template=cj_templates if cj_templates else None,
            error=error,
        )

    def _process_items(
        self, items: Sequence[Any], href_factory: Callable[[Any], str] | None
    ) -> list[Item]:
        cj_items: list[Item] = []
        for item in items:
            if isinstance(item, Item):
                cj_items.append(item)
            elif hasattr(item, "to_cj_data"):
                href = href_factory(item) if href_factory else ""
                cj_items.append(item.to_cj_data(href=href))
        return cj_items

    def _process_links(
        self, links: Sequence[str | Link | tuple[Any, ...] | Callable[..., Any]]
    ) -> list[Link]:
        cj_links: list[Link] = []
        for link in links:
            if isinstance(link, Link):
                cj_links.append(link)
            else:
                transition, rel = self._resolve_transition(link)
                if transition:
                    cj_links.append(transition.to_link(rel=rel))
        return cj_links

    def _process_queries(
        self, queries: Sequence[str | Query | tuple[Any, ...] | Callable[..., Any]]
    ) -> list[Query]:
        cj_queries: list[Query] = []
        for query in queries:
            if isinstance(query, Query):
                cj_queries.append(query)
            else:
                transition, rel = self._resolve_transition(query)
                if transition:
                    q = transition.to_query()
                    if rel:
                        q.rel = rel
                    cj_queries.append(q)
        return cj_queries

    def _process_templates(
        self, templates: Sequence[str | Template | tuple[Any, ...] | Callable[..., Any]]
    ) -> list[Template]:
        cj_templates: list[Template] = []
        for template in templates:
            if isinstance(template, Template):
                cj_templates.append(template)
            else:
                transition, rel = self._resolve_transition(template)
                if transition:
                    t = transition.to_template()
                    if rel:
                        t.rel = rel
                    cj_templates.append(t)
        return cj_templates

    def _resolve_transition(self, arg: Any) -> tuple[Any, str | None]:
        name: str | Callable[..., Any]
        rel: str | None = None
        params: dict[str, Any] = {}

        if isinstance(arg, str) or callable(arg):
            name = arg
        elif isinstance(arg, tuple):
            if len(arg) == 2:
                if isinstance(arg[1], dict):
                    name, params = arg
                else:
                    name, rel = arg
            elif len(arg) == 3:
                name, rel, params = arg
            else:
                return None, None
        else:
            return None, None

        transition = self.tm.get_transition(name, params)
        return transition, rel
