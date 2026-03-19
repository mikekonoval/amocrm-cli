"""CLI commands for users and roles resources."""
from __future__ import annotations

from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.users import UsersResource, RolesResource

app = typer.Typer(name="users", help="Manage users")
roles_app = typer.Typer(name="roles", help="Manage roles")
app.add_typer(roles_app)


def _get_users_resource() -> UsersResource:
    return UsersResource(AmoCRMClient())


def _get_roles_resource() -> RolesResource:
    return RolesResource(AmoCRMClient())


# Users commands
@app.command("list")
def list_users(
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(50, "--limit"),
    with_: Optional[str] = typer.Option(None, "--with"),
    output: str = typer.Option("table", "--output"),
    columns: Optional[str] = typer.Option(None, "--columns"),
) -> None:
    """List users."""
    try:
        with_list = with_.split(",") if with_ else None
        cols = columns.split(",") if columns else None
        resource = _get_users_resource()
        results = resource.list(page=page, limit=limit, with_=with_list)
        render(results, output=output, columns=cols)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("get")
def get_user(
    id: int = typer.Argument(...),
    with_: Optional[str] = typer.Option(None, "--with"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Get a user by ID."""
    try:
        with_list = with_.split(",") if with_ else None
        resource = _get_users_resource()
        result = resource.get(id, with_=with_list)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


# Roles commands
@roles_app.command("list")
def list_roles(
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(50, "--limit"),
    with_: Optional[str] = typer.Option(None, "--with"),
    output: str = typer.Option("table", "--output"),
    columns: Optional[str] = typer.Option(None, "--columns"),
) -> None:
    """List roles."""
    try:
        with_list = with_.split(",") if with_ else None
        cols = columns.split(",") if columns else None
        resource = _get_roles_resource()
        results = resource.list(page=page, limit=limit, with_=with_list)
        render(results, output=output, columns=cols)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@roles_app.command("get")
def get_role(
    id: int = typer.Argument(...),
    with_: Optional[str] = typer.Option(None, "--with"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Get a role by ID."""
    try:
        with_list = with_.split(",") if with_ else None
        resource = _get_roles_resource()
        result = resource.get(id, with_=with_list)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
