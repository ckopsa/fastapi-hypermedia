from abc import ABC, abstractmethod
from typing import Any

from fastapi.requests import Request
from fastapi.templating import Jinja2Templates


class HtmlRendererInterface(ABC):
    @abstractmethod
    async def render(self, template_name: str, request: Request, context: dict[str, Any]) -> str:
        pass


class Jinja2HtmlRenderer(HtmlRendererInterface):
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates

    async def render(self, template_name: str, request: Request, context: dict[str, Any]) -> str:
        return self.templates.TemplateResponse(template_name, {"request": request, **context})
