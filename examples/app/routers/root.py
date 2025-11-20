from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from fastapi_hypermedia import Hypermedia

from ..core.representor import Representor
from ..core.security import AuthenticatedUser, get_current_user
from ..dependencies import get_hypermedia, get_representor

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def healthcheck() -> dict[str, str]:
    """API endpoint for health check."""
    return {"status": "ok"}


@router.get(
    "/",
    tags=["collection"],
    response_class=HTMLResponse,
    operation_id="home",
    responses={
        200: {
            "content": {"application/vnd.collection+json": {}, "text/html": {}},
        }
    },
)
async def home(
    request: Request,
    current_user: AuthenticatedUser | None = Depends(get_current_user),
    hypermedia: Hypermedia = Depends(get_hypermedia),
    representor: Representor = Depends(get_representor),
) -> Any:
    """Serves the homepage."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    return await representor.represent(
        hypermedia.create_collection_json(
            title="Home",
            links=[
                "home",
                "get_workflow_definitions",
                "get_workflow_instances",
            ],
        )
    )
