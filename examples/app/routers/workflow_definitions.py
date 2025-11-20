from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from fastapi_hypermedia import Hypermedia
from fastapi_hypermedia.cj_models import CollectionJson

from .. import models
from ..core.representor import Representor
from ..core.security import AuthenticatedUser, get_current_user
from ..dependencies import (
    get_hypermedia,
    get_representor,
    get_workflow_service,
)
from ..schemas.hypermedia import WorkflowItem
from ..services import WorkflowService

router = APIRouter(
    prefix="/workflow-definitions",
    tags=["workflow-definitions"],
    responses={
        200: {
            "content": {"application/vnd.collection+json": {}, "text/html": {}},
        }
    },
)


@router.get(
    "/",
    response_model=CollectionJson,
    summary="Workflow Definitions",
    tags=["collection"],
)
async def get_workflow_definitions(
    request: Request,
    current_user: AuthenticatedUser | None = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service),
    representor: Representor = Depends(get_representor),
    hypermedia: Hypermedia = Depends(get_hypermedia),
) -> Any:
    """Returns a Collection+JSON representation of workflow definitions."""
    if isinstance(current_user, RedirectResponse):
        return current_user
    assert current_user is not None
    workflow_definitions: list[
        models.WorkflowDefinition
    ] = await service.list_workflow_definitions()

    items = [
        WorkflowItem.from_entity(d, request, hypermedia.tm)
        for d in workflow_definitions
    ]

    cj = hypermedia.create_collection_json(
        title="Workflow Definitions",
        links=[
            "home",
            "get_workflow_instances",
            "get_workflow_definitions",
            "simple_create_workflow_definition_form",
        ],
        items=items,
    )

    return await representor.represent(cj)


@router.post(
    "/{definition_id}/createInstance",
    summary="Create Workflow Instance",
    tags=["create", "workflow-instances"],
)
async def create_workflow_instance_from_definition(
    definition_id: str,
    current_user: AuthenticatedUser | None = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service),
) -> Any:
    if isinstance(current_user, RedirectResponse):
        return current_user

    assert current_user is not None
    definitions = await service.list_workflow_definitions(definition_id=definition_id)
    if not definitions:
        return HTMLResponse(status_code=404, content="Workflow Definition not found")
    definition = definitions[0]
    new_instance = await service.create_workflow_instance(
        models.WorkflowInstance(
            workflow_definition_id=definition_id,
            user_id=current_user.user_id,
            name=definition.name,
            due_datetime=definition.due_datetime,
        )
    )
    assert new_instance is not None

    return RedirectResponse(
        url=f"/workflow-instances/{new_instance.id}",  # Placeholder URL
        status_code=303,
    )


@router.get(
    "/{definition_id}",
    response_model=CollectionJson,
    summary="View Workflow Definition",
    tags=["item"],
)
async def view_workflow_definition(
    request: Request,
    definition_id: str,
    current_user: AuthenticatedUser | None = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service),
    representor: Representor = Depends(get_representor),
    hypermedia: Hypermedia = Depends(get_hypermedia),
) -> Any:
    """Returns a Collection+JSON representation of a specific workflow definition."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    assert current_user is not None
    workflow_definition: list[
        models.WorkflowDefinition
    ] = await service.list_workflow_definitions(definition_id=definition_id)
    if not workflow_definition:
        return HTMLResponse(status_code=404, content="Workflow Definition not found")

    first_workflow_definition: models.WorkflowDefinition = workflow_definition[0]
    templates = []
    if t1 := hypermedia.tm.get_transition(
        "create_workflow_instance_from_definition", {"definition_id": definition_id}
    ):
        templates.append(t1.to_template())
    if t2 := hypermedia.tm.get_transition("simple_create_workflow_definition", {}):
        templates.append(
            t2.to_template(
                {
                    "id": first_workflow_definition.id,
                    "name": first_workflow_definition.name,
                    "description": first_workflow_definition.description,
                    "task_definitions": "\n".join(
                        task.name for task in first_workflow_definition.task_definitions
                    ),
                }
            )
        )

    items_list: list[Any] = []
    items_list.extend(workflow_definition)
    items_list.extend(workflow_definition[0].task_definitions)

    cj = hypermedia.create_collection_json(
        title="View Workflow Definition",
        links=[
            "home",
            "get_workflow_instances",
            "get_workflow_definitions",
        ],
        items=items_list,
        item_href=lambda item: str(
            request.url_for("view_workflow_definition", definition_id=definition_id)
        ),
        templates=templates,
    )

    return await representor.represent(cj)


@router.post(
    "/{definition_id}",
    response_model=CollectionJson,
    summary="Create Workflow Definition Form",
    tags=["create"],
)
async def create_workflow_definition(
    request: Request,
    definition_id: str,
    workflow_definition_task: Annotated[models.TaskDefinitionBase, Form()],
    service: WorkflowService = Depends(get_workflow_service),
    current_user: AuthenticatedUser | None = Depends(get_current_user),
) -> Any:
    """Returns a form to create a new workflow definition in Collection+JSON format."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    assert current_user is not None
    definitions = await service.list_workflow_definitions(definition_id=definition_id)
    if not definitions:
        return HTMLResponse(status_code=404, content="Workflow Definition not found")

    definition = definitions[0]  # Assuming single definition returned
    # Create a task for the new workflow definition
    await service.update_definition(
        definition_id=definition.id,
        name=definition.name,
        description=definition.description,
        task_definitions=definition.task_definitions + [workflow_definition_task],
    )

    return RedirectResponse(
        url=str(
            request.url_for("view_workflow_definition", definition_id=definition.id)
        ),
        status_code=303,
    )


@router.post(
    "/",
    response_model=CollectionJson,
    summary="Create Workflow Definition",
)
async def cj_create_workflow_definition(
    request: Request,
    definition: Annotated[models.WorkflowDefinitionCreateRequest, Form()],
    current_user: AuthenticatedUser | None = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service),
) -> Any:
    """Creates a new workflow definition and returns it in Collection+JSON format."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    created_definition = await service.create_new_definition(
        name=definition.name, description=definition.description, task_definitions=[]
    )

    return RedirectResponse(
        url=str(
            request.url_for(
                "view_workflow_definition", definition_id=created_definition.id
            )
        ),
        status_code=303,
    )


@router.get(
    "-simpleForm",
    response_model=CollectionJson,
    summary="Create Workflow Definition",
)
async def simple_create_workflow_definition_form(
    request: Request,
    current_user: AuthenticatedUser | None = Depends(get_current_user),
    representor: Representor = Depends(get_representor),
    hypermedia: Hypermedia = Depends(get_hypermedia),
) -> Any:
    """Returns a Collection+JSON representation of a form to create a new workflow definition."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    assert current_user is not None

    t = hypermedia.tm.get_transition("simple_create_workflow_definition", {})
    template = (
        [
            t.to_template(
                defaults=models.SimpleWorkflowDefinitionCreateRequest().model_dump()
            )
        ]
        if t
        else []
    )

    cj = hypermedia.create_collection_json(
        title="Create Workflow Definition",
        links=[
            "home",
            "get_workflow_definitions",
        ],
        templates=template,
    )

    return await representor.represent(cj)


@router.post(
    "-simpleForm",
    response_model=CollectionJson,
    summary="Create Workflow Definition",
)
async def simple_create_workflow_definition(
    request: Request,
    definition: Annotated[models.SimpleWorkflowDefinitionCreateRequest, Form()],
    current_user: AuthenticatedUser | None = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service),
) -> Any:
    """Creates a new workflow definition and returns it in Collection+JSON format."""
    if isinstance(current_user, RedirectResponse):
        return current_user

    task_definitions = []
    for order, task_name in enumerate(
        definition.task_definitions.splitlines(), start=1
    ):
        if task_name.strip():
            print(order)
            task_definitions.append(
                models.TaskDefinitionBase(
                    name=task_name.strip(), order=order, due_datetime_offset_minutes=0
                )
            )

    if not await service.list_workflow_definitions(definition_id=definition.id):
        created_definition = await service.create_new_definition(
            name=definition.name,
            description=definition.description,
            task_definitions=task_definitions,
        )
    else:
        created_definition = await service.update_definition(
            definition_id=definition.id,
            name=definition.name,
            description=definition.description,
            task_definitions=task_definitions,
        )
    assert created_definition is not None
    return RedirectResponse(
        url=str(
            request.url_for(
                "view_workflow_definition", definition_id=created_definition.id
            )
        ),
        status_code=303,
    )
