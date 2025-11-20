from typing import Any

from fastapi.responses import JSONResponse

from .cj_models import CollectionJson


class CollectionResponse(JSONResponse):
    media_type = "application/vnd.collection+json"

    def __init__(self, content: CollectionJson | dict[str, Any], **kwargs: Any) -> None:
        if isinstance(content, CollectionJson):
            content = content.model_dump(exclude_none=True)
        super().__init__(content=content, **kwargs)
