"""CLI commands for leads resource."""
from __future__ import annotations

import json
from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.leads import LeadsResource

app = typer.Typer(name="leads", help="Manage leads")


def _get_resource() -> LeadsResource:
    return LeadsResource(AmoCRMClient())


@app.command("list")
def list_leads(
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(50, "--limit"),
    filter: Optional[str] = typer.Option(None, "--filter", help="JSON filter string"),
    order: Optional[str] = typer.Option(None, "--order"),
    with_: Optional[str] = typer.Option(None, "--with"),
    output: str = typer.Option("table", "--output"),
    columns: Optional[str] = typer.Option(None, "--columns"),
) -> None:
    """List leads."""
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
def get_lead(
    id: int = typer.Argument(...),
    with_: Optional[str] = typer.Option(None, "--with"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Get a lead by ID."""
    try:
        with_list = with_.split(",") if with_ else None
        resource = _get_resource()
        result = resource.get(id, with_=with_list)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("create")
def create_lead(
    name: str = typer.Option(..., "--name"),
    price: Optional[int] = typer.Option(None, "--price"),
    pipeline_id: Optional[int] = typer.Option(None, "--pipeline-id"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Create a new lead."""
    try:
        data: dict = {"name": name}
        if price is not None:
            data["price"] = price
        if pipeline_id is not None:
            data["pipeline_id"] = pipeline_id
        resource = _get_resource()
        results = resource.create([data])
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("delete")
def delete_lead(
    id: int = typer.Argument(...),
) -> None:
    """Delete a lead by ID."""
    try:
        resource = _get_resource()
        resource.delete(id)
        typer.echo(f"Lead {id} deleted.")
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
