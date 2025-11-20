import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from fastapi_hypermedia import cj_models

from .db_models.enums import TaskStatus, WorkflowStatus

__all__ = [
    "TaskDefinitionBase",
    "TaskInstance",
    "SimpleTaskInstance",
    "WorkflowInstance",
    "WorkflowDefinition",
    "WorkflowDefinitionCreateRequest",
    "SimpleWorkflowDefinitionCreateRequest",
    "WorkflowInstanceCreateRequest",
    "TaskStatus",
    "WorkflowStatus",
]


class TaskDefinitionBase(BaseModel):
    name: str = Field(
        ...,
        description="Name of the task",
        title="Task Name",
        examples=["Review Document", "Approve Budget"],
    )
    order: int = Field(
        ...,
        description="Order of the task in the workflow",
        title="Task Order",
        json_schema_extra={"x-render-hint": "hidden"},
    )
    due_datetime_offset_minutes: int | None = Field(
        0,
        description="Offset in minutes for the task's due date from the workflow instance's due date",
        title="Due Date Offset",
        json_schema_extra={"x-render-hint": "hidden"},
    )

    def to_cj_data(
        self, href: str = "", links: list[cj_models.Link] | None = None, rel: str = "item"
    ) -> cj_models.Item:
        return cj_models.to_collection_json_data(self, href, links, rel)


class TaskInstance(BaseModel):
    id: str = Field(default_factory=lambda: "task_" + str(uuid.uuid4())[:8])
    workflow_instance_id: str
    name: str
    order: int
    status: TaskStatus = TaskStatus.pending
    due_datetime: datetime | None = None  # New field

    class Config:
        from_attributes = True


class SimpleTaskInstance(BaseModel):
    id: str = Field(..., json_schema_extra={"x-render-hint": "hidden"})
    name: str
    order: int = Field(..., json_schema_extra={"x-render-hint": "hidden"})
    status: TaskStatus = TaskStatus.pending

    def to_cj_data(
        self, href: str = "", links: list[cj_models.Link] | None = None, rel: str = "item"
    ) -> cj_models.Item:
        return cj_models.to_collection_json_data(self, href, links, rel)

    @staticmethod
    def from_task_instance(task_instance: TaskInstance) -> "SimpleTaskInstance":
        return SimpleTaskInstance(
            id=task_instance.id,
            name=task_instance.name,
            order=task_instance.order,
            status=task_instance.status,
        )


class WorkflowInstance(BaseModel):
    id: str = Field(
        default_factory=lambda: "wf_" + str(uuid.uuid4())[:8],
        json_schema_extra={"x-render-hint": "hidden"},
    )
    workflow_definition_id: str = Field(
        ..., json_schema_extra={"x-render-hint": "hidden"}
    )
    name: str | None = None  # Made name optional
    user_id: str = Field(..., json_schema_extra={"x-render-hint": "hidden"})
    status: WorkflowStatus = WorkflowStatus.active
    created_at: datetime = Field(default_factory=datetime.utcnow)
    share_token: str | None = Field(None, json_schema_extra={"x-render-hint": "hidden"})
    due_datetime: datetime | None = Field(
        None, json_schema_extra={"x-render-hint": "hidden"}
    )
    tasks: list[TaskInstance] = Field(
        default_factory=list, json_schema_extra={"x-render-hint": "hidden"}
    )

    def to_cj_data(
        self, href: str = "", links: list[cj_models.Link] | None = None, rel: str = "item"
    ) -> cj_models.Item:
        return cj_models.to_collection_json_data(self, href, links, rel)

    class Config:
        from_attributes = True


class WorkflowDefinition(BaseModel):
    id: str = Field(
        default_factory=lambda: "def_" + str(uuid.uuid4())[:8],
        json_schema_extra={"x-render-hint": "hidden"},
    )
    name: str
    description: str | None = ""
    task_definitions: list[TaskDefinitionBase] = Field(
        default_factory=list, json_schema_extra={"x-render-hint": "hidden"}
    )
    due_datetime: datetime | None = Field(
        None, json_schema_extra={"x-render-hint": "hidden"}
    )

    def to_cj_data(
        self, href: str = "", links: list[cj_models.Link] | None = None, rel: str = "item"
    ) -> cj_models.Item:
        return cj_models.to_collection_json_data(self, href, links, rel)

    class Config:
        from_attributes = True


class WorkflowDefinitionCreateRequest(BaseModel):
    name: str
    description: str | None = ""


class SimpleWorkflowDefinitionCreateRequest(BaseModel):
    id: str = Field(
        default_factory=lambda: "def_" + str(uuid.uuid4())[:8],
        json_schema_extra={"x-render-hint": "hidden"},
    )
    name: str = "New Workflow Definition"
    description: str | None = ""
    task_definitions: str = Field(
        "1. Task One\n2. Task Two\n3. Task Three",
        description="Newline-separated list of task names",
        title="Task Definitions",
        json_schema_extra={
            "x-render-hint": "textarea",
        },
    )


class WorkflowInstanceCreateRequest(BaseModel):
    definition_id: str
    name: str | None = None
