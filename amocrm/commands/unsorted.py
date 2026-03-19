# amocrm/commands/unsorted.py
"""CLI commands for unsorted leads."""
from __future__ import annotations

import json
from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.unsorted import UnsortedResource

app = typer.Typer(name="unsorted", help="Manage unsorted leads")


def _get_resource() -> UnsortedResource:
    return UnsortedResource(AmoCRMClient())


@app.command("list")
def list_unsorted(
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(50, "--limit"),
    filter: Optional[str] = typer.Option(None, "--filter", help="JSON filter string"),
    output: str = typer.Option("table", "--output"),
    columns: Optional[str] = typer.Option(None, "--columns"),
) -> None:
    """List unsorted leads."""
    try:
        filters = json.loads(filter) if filter else None
        cols = columns.split(",") if columns else None
        results = _get_resource().list(page=page, limit=limit, filters=filters)
        render(results, output=output, columns=cols)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    except json.JSONDecodeError:
        typer.echo("Invalid JSON in --filter", err=True)
        raise typer.Exit(1)


@app.command("get")
def get_unsorted(
    uid: str = typer.Argument(..., help="Unsorted lead UID"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Get an unsorted lead by UID."""
    try:
        result = _get_resource().get_by_uid(uid)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("accept")
def accept_unsorted(
    uid: str = typer.Argument(..., help="Unsorted lead UID"),
    pipeline_id: int = typer.Option(..., "--pipeline-id"),
    status_id: int = typer.Option(..., "--status-id"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Accept an unsorted lead into a pipeline."""
    try:
        results = _get_resource().accept([{"uid": uid, "pipeline_id": pipeline_id, "status_id": status_id}])
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("decline")
def decline_unsorted(
    uid: str = typer.Argument(..., help="Unsorted lead UID"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Decline (reject) an unsorted lead."""
    try:
        results = _get_resource().decline([{"uid": uid}])
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
