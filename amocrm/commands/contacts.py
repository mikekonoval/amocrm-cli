"""CLI commands for contacts resource."""
from __future__ import annotations

import json
from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.contacts import ContactsResource

app = typer.Typer(name="contacts", help="Manage contacts")


def _get_resource() -> ContactsResource:
    return ContactsResource(AmoCRMClient())


@app.command("list")
def list_contacts(
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(50, "--limit"),
    filter: Optional[str] = typer.Option(None, "--filter", help="JSON filter string"),
    order: Optional[str] = typer.Option(None, "--order"),
    with_: Optional[str] = typer.Option(None, "--with"),
    output: str = typer.Option("table", "--output"),
    columns: Optional[str] = typer.Option(None, "--columns"),
) -> None:
    """List contacts."""
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
def get_contact(
    id: int = typer.Argument(...),
    with_: Optional[str] = typer.Option(None, "--with"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Get a contact by ID."""
    try:
        with_list = with_.split(",") if with_ else None
        resource = _get_resource()
        result = resource.get(id, with_=with_list)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("create")
def create_contact(
    name: str = typer.Option(..., "--name"),
    email: Optional[str] = typer.Option(None, "--email"),
    phone: Optional[str] = typer.Option(None, "--phone"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Create a new contact."""
    try:
        data: dict = {"name": name}
        if email is not None:
            data["email"] = email
        if phone is not None:
            data["phone"] = phone
        resource = _get_resource()
        results = resource.create([data])
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("delete")
def delete_contact(
    id: int = typer.Argument(...),
) -> None:
    """Delete a contact by ID."""
    try:
        resource = _get_resource()
        resource.delete(id)
        typer.echo(f"Contact {id} deleted.")
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
