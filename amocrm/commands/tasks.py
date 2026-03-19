"""CLI commands for tasks resource."""
from __future__ import annotations

import json
from typing import Any, Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.tasks import TasksResource

app = typer.Typer(name="tasks", help="Manage tasks")


def _get_resource() -> TasksResource:
    return TasksResource(AmoCRMClient())


@app.command("list")
def list_tasks(
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(50, "--limit"),
    filter: Optional[str] = typer.Option(None, "--filter", help="JSON filter string"),
    order: Optional[str] = typer.Option(None, "--order"),
    with_: Optional[str] = typer.Option(None, "--with"),
    output: str = typer.Option("table", "--output"),
    columns: Optional[str] = typer.Option(None, "--columns"),
) -> None:
    """List tasks."""
    try:
        filters = json.loads(filter) if filter else None
        with_list = with_.split(",") if with_ else None
        cols = columns.split(",") if columns else None
        resource = _get_resource()
        results = resource.list(page=page, limit=limit, filters=filters, order=order, with_=with_list)
        render(results, output=output, columns=cols)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    except json.JSONDecodeError:
        typer.echo("Invalid JSON in --filter", err=True)
        raise typer.Exit(1)


@app.command("get")
def get_task(
    id: int = typer.Argument(...),
    with_: Optional[str] = typer.Option(None, "--with"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Get a task by ID."""
    try:
        with_list = with_.split(",") if with_ else None
        resource = _get_resource()
        result = resource.get(id, with_=with_list)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("create")
def create_task(
    text: str = typer.Option(..., "--text"),
    complete_till: int = typer.Option(..., "--complete-till"),
    entity_id: Optional[int] = typer.Option(None, "--entity-id"),
    entity_type: str = typer.Option("leads", "--entity-type"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Create a new task."""
    try:
        data: dict[str, Any] = {
            "text": text,
            "complete_till": complete_till,
        }
        if entity_id is not None:
            data["entity_id"] = entity_id
        data["entity_type"] = entity_type
        resource = _get_resource()
        results = resource.create([data])
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("update")
def update_task(
    id: int = typer.Argument(...),
    text: Optional[str] = typer.Option(None, "--text"),
    complete_till: Optional[int] = typer.Option(None, "--complete-till", help="Unix timestamp"),
    is_completed: Optional[bool] = typer.Option(None, "--is-completed"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Update a task by ID."""
    try:
        data: dict[str, object] = {}
        if text is not None:
            data["text"] = text
        if complete_till is not None:
            data["complete_till"] = complete_till
        if is_completed is not None:
            data["is_completed"] = is_completed
        if not data:
            typer.echo("Provide at least one field to update.", err=True)
            raise typer.Exit(1)
        resource = _get_resource()
        result = resource.update(id, data)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("delete")
def delete_task(
    id: int = typer.Argument(...),
) -> None:
    """Delete a task by ID."""
    try:
        resource = _get_resource()
        resource.delete(id)
        typer.echo(f"Task {id} deleted.")
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
