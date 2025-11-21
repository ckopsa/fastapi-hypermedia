from fastapi import Request
from fastapi.responses import JSONResponse, Response

from fastapi_hypermedia import cj_models

from .html_renderer import HtmlRendererInterface


class Representor:
    def __init__(
        self,
        request: Request,
        html_renderer: HtmlRendererInterface,
    ) -> None:
        self.request = request
        self.html_renderer = html_renderer

    async def represent(self, collection_json: cj_models.CollectionJson) -> Response:
        accept_preferences = self.request.headers.get("Accept", "")
        accept_list = accept_preferences.split(",")
        for item in accept_list:
            match item.strip():
                case "application/vnd.collection+json":
                    return JSONResponse(
                        content=collection_json.model_dump(),
                        headers={"Content-Type": "application/vnd.collection+json"},
                    )
        # Use template-based rendering
        return await self.html_renderer.render(
            "future.html",
            self.request,
            {
                "collection": collection_json.collection,
                "request": self.request,
                "template": collection_json.template,
            },
        )
