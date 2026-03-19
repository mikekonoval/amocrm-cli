"""CLI commands for events resource."""
from __future__ import annotations

import json
from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.events import EventsResource

app = typer.Typer(name="events", help="View events")


@app.command("list")
def list_events(
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
        resource = EventsResource(AmoCRMClient())
        results = resource.list(page=page, limit=limit, filters=filters, order=order)
        render(results, output=output, columns=cols)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    except json.JSONDecodeError:
        typer.echo("Invalid JSON in --filter", err=True)
        raise typer.Exit(1)


@app.command("get")
def get_event(
    id: int = typer.Argument(...),
    output: str = typer.Option("table", "--output"),
) -> None:
    try:
        resource = EventsResource(AmoCRMClient())
        result = resource.get(id)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
