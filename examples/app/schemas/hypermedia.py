from __future__ import annotations

from fastapi import Request

from fastapi_hypermedia import cj_models, transitions

from .. import models  # Your domain models


class WorkflowItem(cj_models.Item):
    """
    A Pydantic model representing a Workflow in Collection+JSON format.
    Inherits from the generic Item model but adds specific construction logic.
    """

    @classmethod
    def from_entity(
        cls,
        workflow: models.WorkflowDefinition,
        request: Request,
        tm: transitions.TransitionManager,
    ) -> WorkflowItem:
        """
        Factory method to build the Hypermedia Item from a domain entity.
        """
        # 1. Generate Self Link
        href = str(
            request.url_for("view_workflow_definition", definition_id=workflow.id)
        )

        # 2. Define Transitions (Business Logic for Links)
        # You can add conditionals here (e.g., if user.is_admin...)
        transition_configs = [
            ("view_workflow_definition", {"definition_id": workflow.id}),
            (
                "create_workflow_instance_from_definition",
                {"definition_id": workflow.id},
            ),
        ]

        transitions = [
            tm.get_transition(name, params) for name, params in transition_configs
        ]
        links = [t.to_link() for t in transitions if t]

        # 3. Use the existing helper or manual construction
        # This reuses the logic you already have in cj_models.py
        base_item = workflow.to_cj_data(href=href, links=links)

        # Return an instance of this class
        return cls(
            href=base_item.href,
            rel=base_item.rel,
            data=base_item.data,
            links=base_item.links,
        )


class WorkflowInstanceItem(cj_models.Item):
    """
    A Pydantic model representing a WorkflowInstance in Collection+JSON format.
    """

    @classmethod
    def from_entity(
        cls,
        workflow: models.WorkflowInstance,
        request: Request,
        tm: transitions.TransitionManager,
    ) -> WorkflowInstanceItem:
        """
        Factory method to build the Hypermedia Item from a domain entity.
        """
        # 1. Generate Self Link
        href = str(request.url_for("view_workflow_instance", instance_id=workflow.id))

        # 2. Define Transitions based on status
        transition_configs = [
            ("view_workflow_instance", {"instance_id": workflow.id}),
        ]

        if workflow.status != models.WorkflowStatus.archived:
            transition_configs.append(
                ("archive_workflow_instance", {"instance_id": workflow.id})
            )

        transitions = [
            tm.get_transition(name, params) for name, params in transition_configs
        ]
        links = [t.to_link() for t in transitions if t]

        # 3. Build item
        base_item = workflow.to_cj_data(href=href, links=links)

        return cls(
            href=base_item.href,
            rel=base_item.rel,
            data=base_item.data,
            links=base_item.links,
        )


class TaskItem(cj_models.Item):
    """
    A Pydantic model representing a TaskInstance in Collection+JSON format.
    """

    @classmethod
    def from_entity(
        cls,
        task: models.SimpleTaskInstance,
        request: Request,
        tm: transitions.TransitionManager,
        instance_id: str,
    ) -> TaskItem:
        """
        Factory method to build the Hypermedia Item from a domain entity.
        """
        # 1. Generate Link to the workflow instance (tasks don't have individual pages)
        href = str(request.url_for("view_workflow_instance", instance_id=instance_id))

        # 2. Define Transitions based on task status
        transition_configs = []
        if task.status == models.TaskStatus.completed:
            transition_configs.append(("reopen_task_instance", {"task_id": task.id}))
        else:
            transition_configs.append(("complete_task_instance", {"task_id": task.id}))

        transitions = [
            tm.get_transition(name, params) for name, params in transition_configs
        ]
        links = [t.to_link() for t in transitions if t]

        # 3. Build item
        base_item = task.to_cj_data(href=href, links=links)

        return cls(
            href=base_item.href,
            rel=base_item.rel,
            data=base_item.data,
            links=base_item.links,
        )
