"""CLI commands for tags resource."""
from __future__ import annotations

import json
from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.tags import TagsResource

app = typer.Typer(name="tags", help="Manage tags")


@app.command("list")
def list_tags(
    entity: str = typer.Option(..., "--entity", help="Entity type: leads, contacts, companies"),
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(50, "--limit"),
    filter: Optional[str] = typer.Option(None, "--filter"),
    order: Optional[str] = typer.Option(None, "--order"),
    output: str = typer.Option("table", "--output"),
    columns: Optional[str] = typer.Option(None, "--columns"),
) -> None:
    try:
        filters = json.loads(filter) if filter else None
        cols = columns.split(",") if columns else None
        resource = TagsResource(AmoCRMClient(), entity_type=entity)
        results = resource.list(page=page, limit=limit, filters=filters, order=order)
        render(results, output=output, columns=cols)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    except json.JSONDecodeError:
        typer.echo("Invalid JSON in --filter", err=True)
        raise typer.Exit(1)


@app.command("get")
def get_tag(
    id: int = typer.Argument(...),
    entity: str = typer.Option(..., "--entity"),
    output: str = typer.Option("table", "--output"),
) -> None:
    try:
        resource = TagsResource(AmoCRMClient(), entity_type=entity)
        result = resource.get(id)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("create")
def create_tag(
    entity: str = typer.Option(..., "--entity"),
    name: str = typer.Option(..., "--name"),
    color: Optional[str] = typer.Option(None, "--color"),
    output: str = typer.Option("table", "--output"),
) -> None:
    try:
        resource = TagsResource(AmoCRMClient(), entity_type=entity)
        data = {"name": name}
        if color:
            data["color"] = color
        results = resource.create([data])
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("update")
def update_tag(
    id: int = typer.Argument(...),
    entity: str = typer.Option(..., "--entity", help="Entity type: leads, contacts, companies"),
    name: str = typer.Option(..., "--name"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Update a tag by ID."""
    try:
        resource = TagsResource(AmoCRMClient(), entity_type=entity)
        result = resource.update(id, {"name": name})
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("delete")
def delete_tag(
    id: int = typer.Argument(...),
    entity: str = typer.Option(..., "--entity"),
) -> None:
    try:
        resource = TagsResource(AmoCRMClient(), entity_type=entity)
        resource.delete(id)
        typer.echo(f"Tag {id} deleted.")
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
