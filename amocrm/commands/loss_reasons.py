# amocrm/commands/loss_reasons.py
"""CLI commands for loss reasons resource."""
from __future__ import annotations

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.loss_reasons import LossReasonsResource

app = typer.Typer(name="loss-reasons", help="Manage lead loss reasons")


def _get_resource() -> LossReasonsResource:
    return LossReasonsResource(AmoCRMClient())


@app.command("list")
def list_reasons(
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(50, "--limit"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """List loss reasons."""
    try:
        results = _get_resource().list(page=page, limit=limit)
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("get")
def get_reason(
    id: int = typer.Argument(...),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Get a loss reason by ID."""
    try:
        result = _get_resource().get(id)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("create")
def create_reason(
    name: str = typer.Option(..., "--name"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Create a loss reason."""
    try:
        results = _get_resource().create([{"name": name}])
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("update")
def update_reason(
    id: int = typer.Argument(...),
    name: str = typer.Option(..., "--name"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Update a loss reason by ID."""
    try:
        result = _get_resource().update(id, {"name": name})
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("delete")
def delete_reason(
    id: int = typer.Argument(...),
) -> None:
    """Delete a loss reason by ID."""
    try:
        _get_resource().delete(id)
        typer.echo(f"Loss reason {id} deleted.")
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
