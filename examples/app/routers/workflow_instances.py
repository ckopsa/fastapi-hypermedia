from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from fastapi_hypermedia import cj_models, transitions
from fastapi_hypermedia.cj_models import CollectionJson

from .. import models
from ..core.representor import Representor
from ..core.security import AuthenticatedUser, get_current_user
from ..dependencies import (
    get_representor,
    get_transition_registry,
    get_workflow_service,
)
from ..schemas.hypermedia import TaskItem, WorkflowInstanceItem
from ..services import WorkflowService

router = APIRouter(
    prefix="/workflow-instances",
    tags=["workflow-instances"],
    responses={
        200: {
            "content": {"application/vnd.collection+json": {}, "text/html": {}},
        }
    },
)


@router.get(
    "/",
    response_model=CollectionJson,
    summary="Workflow Instances",
    tags=["collection"],
)
async def get_workflow_instances(
    request: Request,
    current_user: AuthenticatedUser | None = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service),
    representor: Representor = Depends(get_representor),
    transition_manager: transitions.TransitionManager = Depends(
        get_transition_registry
    ),
) -> Any:
    """Returns a Collection+JSON representation of workflow instances."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    assert current_user is not None
    workflow_instances: list[
        models.WorkflowInstance
    ] = await service.list_instances_for_user(user_id=current_user.user_id)

    items = [
        WorkflowInstanceItem.from_entity(d, request, transition_manager)
        for d in workflow_instances
    ]

    collection = cj_models.Collection(
        href=str(request.url),
        title="Workflow Instances",
        links=[
            t.to_link()
            for t in [
                transition_manager.get_transition("home", {}),
                transition_manager.get_transition("get_workflow_instances", {}),
                transition_manager.get_transition("get_workflow_definitions", {}),
            ]
            if t
        ],
        items=items,
    )

    return await representor.represent(
        cj_models.CollectionJson(
            collection=collection,
            template=[],
            error=None,
        )
    )


@router.get(
    "/{instance_id}",
    response_model=CollectionJson,
    summary="View Workflow Instance",
    tags=["item"],
)
async def view_workflow_instance(
    request: Request,
    instance_id: str,
    current_user: AuthenticatedUser | None = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service),
    representor: Representor = Depends(get_representor),
    transition_manager: transitions.TransitionManager = Depends(
        get_transition_registry
    ),
) -> Any:
    """Returns a Collection+JSON representation of a specific workflow instance."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    assert current_user is not None
    workflow_instance = await service.get_workflow_instance_with_tasks(
        instance_id=instance_id, user_id=current_user.user_id
    )
    if not workflow_instance:
        return HTMLResponse(status_code=404, content="Workflow Instance not found")

    page_transitions = [
        transition_manager.get_transition("home", {}),
        transition_manager.get_transition("get_workflow_instances", {}),
        transition_manager.get_transition("get_workflow_definitions", {}),
        transition_manager.get_transition(
            "view_workflow_definition",
            {"definition_id": workflow_instance.workflow_definition_id},
        ),
    ]

    tasks = workflow_instance.tasks
    # sort by completed last and then order
    tasks.sort(
        key=lambda x: x.order
        if x.status != models.TaskStatus.completed
        else x.order + 100
    )

    items = [
        TaskItem.from_entity(
            models.SimpleTaskInstance.from_task_instance(task),
            request,
            transition_manager,
            instance_id,
        )
        for task in tasks
    ]

    collection = cj_models.Collection(
        href=str(request.url),
        title=f"{workflow_instance.name} - {workflow_instance.status.title()}",
        links=[t.to_link() for t in page_transitions if t],
        items=items,
    )

    return await representor.represent(
        cj_models.CollectionJson(
            collection=collection,
            template=[],
            error=None,
        )
    )


@router.post(
    "-task/{task_id}/complete",
    response_model=CollectionJson,
    summary="Complete Task",
    tags=["edit"],
)
async def complete_task_instance(
    request: Request,
    task_id: str,
    current_user: AuthenticatedUser | None = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service),
) -> Any:
    if isinstance(current_user, RedirectResponse):
        return current_user

    assert current_user is not None
    task_instance = await service.complete_task(
        task_id=task_id, user_id=current_user.user_id
    )
    assert task_instance is not None

    return RedirectResponse(
        url=str(
            request.url_for(
                "view_workflow_instance", instance_id=task_instance.workflow_instance_id
            )
        ),
        status_code=303,
    )


@router.post(
    "-task/{task_id}/reopen",
    response_model=CollectionJson,
    summary="Reopen Task",
    tags=["edit"],
)
async def reopen_task_instance(
    request: Request,
    task_id: str,
    current_user: AuthenticatedUser | None = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service),
) -> Any:
    if isinstance(current_user, RedirectResponse):
        return current_user

    assert current_user is not None
    task_instance = await service.undo_complete_task(
        task_id=task_id, user_id=current_user.user_id
    )
    assert task_instance is not None

    return RedirectResponse(
        url=str(
            request.url_for(
                "view_workflow_instance", instance_id=task_instance.workflow_instance_id
            )
        ),
        status_code=303,
    )


@router.post(
    "/{instance_id}/archive",
    response_model=CollectionJson,
    summary="Archive Workflow Instance",
    tags=["edit"],
)
async def archive_workflow_instance(
    request: Request,
    instance_id: str,
    current_user: AuthenticatedUser | None = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service),
) -> Any:
    if isinstance(current_user, RedirectResponse):
        return current_user

    assert current_user is not None
    workflow_instance = await service.archive_workflow_instance(
        instance_id=instance_id, user_id=current_user.user_id
    )
    assert workflow_instance is not None

    return RedirectResponse(
        url=str(
            request.url_for("view_workflow_instance", instance_id=workflow_instance.id)
        ),
        status_code=303,
    )
