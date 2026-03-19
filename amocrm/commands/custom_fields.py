"""CLI commands for custom fields and custom field groups."""
from __future__ import annotations

from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.custom_fields import CustomFieldsResource, CustomFieldGroupsResource

app = typer.Typer(name="custom-fields", help="Manage custom fields")
groups_app = typer.Typer(name="groups", help="Manage custom field groups")
app.add_typer(groups_app, name="groups")


@app.command("list")
def list_fields(
    entity: str = typer.Option(..., "--entity", help="Entity type: leads, contacts, companies"),
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(50, "--limit"),
    output: str = typer.Option("table", "--output"),
    columns: Optional[str] = typer.Option(None, "--columns"),
) -> None:
    """List custom fields for an entity."""
    try:
        cols = columns.split(",") if columns else None
        resource = CustomFieldsResource(AmoCRMClient(), entity=entity)
        results = resource.list(page=page, limit=limit)
        render(results, output=output, columns=cols)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("get")
def get_field(
    id: int = typer.Argument(...),
    entity: str = typer.Option(..., "--entity", help="Entity type: leads, contacts, companies"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Get a custom field by ID."""
    try:
        resource = CustomFieldsResource(AmoCRMClient(), entity=entity)
        result = resource.get(id)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@groups_app.command("list")
def list_groups(
    entity: str = typer.Option(..., "--entity", help="Entity type: leads, contacts, companies"),
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(50, "--limit"),
    output: str = typer.Option("table", "--output"),
    columns: Optional[str] = typer.Option(None, "--columns"),
) -> None:
    """List custom field groups for an entity."""
    try:
        cols = columns.split(",") if columns else None
        resource = CustomFieldGroupsResource(AmoCRMClient(), entity=entity)
        results = resource.list(page=page, limit=limit)
        render(results, output=output, columns=cols)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@groups_app.command("get")
def get_group(
    id: int = typer.Argument(...),
    entity: str = typer.Option(..., "--entity", help="Entity type: leads, contacts, companies"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Get a custom field group by ID."""
    try:
        resource = CustomFieldGroupsResource(AmoCRMClient(), entity=entity)
        result = resource.get(id)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
