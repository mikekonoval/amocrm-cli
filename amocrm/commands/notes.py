"""CLI commands for notes resource."""
from __future__ import annotations

import json
from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.notes import NotesResource

app = typer.Typer(name="notes", help="Manage notes")


@app.command("list")
def list_notes(
    entity: str = typer.Option(..., "--entity", help="Entity type: leads, contacts, companies"),
    entity_id: Optional[int] = typer.Option(None, "--entity-id"),
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
        resource = NotesResource(AmoCRMClient(), entity_type=entity, entity_id=entity_id)
        results = resource.list(page=page, limit=limit, filters=filters, order=order)
        render(results, output=output, columns=cols)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    except json.JSONDecodeError:
        typer.echo("Invalid JSON in --filter", err=True)
        raise typer.Exit(1)


@app.command("get")
def get_note(
    id: int = typer.Argument(...),
    entity: str = typer.Option(..., "--entity"),
    entity_id: Optional[int] = typer.Option(None, "--entity-id"),
    output: str = typer.Option("table", "--output"),
) -> None:
    try:
        resource = NotesResource(AmoCRMClient(), entity_type=entity, entity_id=entity_id)
        result = resource.get(id)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("create")
def create_note(
    entity: str = typer.Option(..., "--entity"),
    entity_id: int = typer.Option(..., "--entity-id"),
    text: str = typer.Option(..., "--text"),
    note_type: str = typer.Option("common", "--type"),
    output: str = typer.Option("table", "--output"),
) -> None:
    try:
        resource = NotesResource(AmoCRMClient(), entity_type=entity, entity_id=entity_id)
        data = {"note_type": note_type, "params": {"text": text}}
        results = resource.create([data])
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("delete")
def delete_note(
    id: int = typer.Argument(...),
    entity: str = typer.Option(..., "--entity"),
    entity_id: Optional[int] = typer.Option(None, "--entity-id"),
) -> None:
    try:
        resource = NotesResource(AmoCRMClient(), entity_type=entity, entity_id=entity_id)
        resource.delete(id)
        typer.echo(f"Note {id} deleted.")
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
