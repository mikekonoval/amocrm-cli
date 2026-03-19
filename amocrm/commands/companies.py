"""CLI commands for companies resource."""
from __future__ import annotations

import json
from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.companies import CompaniesResource

app = typer.Typer(name="companies", help="Manage companies")


def _get_resource() -> CompaniesResource:
    return CompaniesResource(AmoCRMClient())


@app.command("list")
def list_companies(
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(50, "--limit"),
    filter: Optional[str] = typer.Option(None, "--filter", help="JSON filter string"),
    order: Optional[str] = typer.Option(None, "--order"),
    with_: Optional[str] = typer.Option(None, "--with"),
    output: str = typer.Option("table", "--output"),
    columns: Optional[str] = typer.Option(None, "--columns"),
) -> None:
    """List companies."""
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
def get_company(
    id: int = typer.Argument(...),
    with_: Optional[str] = typer.Option(None, "--with"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Get a company by ID."""
    try:
        with_list = with_.split(",") if with_ else None
        resource = _get_resource()
        result = resource.get(id, with_=with_list)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("create")
def create_company(
    name: str = typer.Option(..., "--name"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Create a new company."""
    try:
        data: dict[str, object] = {"name": name}
        resource = _get_resource()
        results = resource.create([data])
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("update")
def update_company(
    id: int = typer.Argument(...),
    name: Optional[str] = typer.Option(None, "--name"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Update a company by ID."""
    try:
        data: dict[str, object] = {}
        if name is not None:
            data["name"] = name
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
def delete_company(
    id: int = typer.Argument(...),
) -> None:
    """Delete a company by ID."""
    try:
        resource = _get_resource()
        resource.delete(id)
        typer.echo(f"Company {id} deleted.")
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
