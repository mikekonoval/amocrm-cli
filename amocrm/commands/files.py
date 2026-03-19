# amocrm/commands/files.py
"""CLI commands for the AmoCRM Files API."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.files import FilesResource

app = typer.Typer(name="files", help="Manage files in AmoCRM drive", no_args_is_help=True)


@app.callback()
def _callback() -> None:
    """Manage files in AmoCRM drive."""


@app.command("list")
def list_files(
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(50, "--limit"),
    output: str = typer.Option("table", "--output"),
    columns: Optional[str] = typer.Option(None, "--columns"),
) -> None:
    """List uploaded files."""
    try:
        resource = FilesResource(AmoCRMClient())
        results = resource.list(page=page, limit=limit)
        render(results, output=output, columns=columns.split(",") if columns else None)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("get")
def get_file(
    uuid: str = typer.Argument(...),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Get file metadata by UUID."""
    try:
        resource = FilesResource(AmoCRMClient())
        result = resource.get(uuid)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("upload")
def upload_file(
    file_path: str = typer.Argument(..., metavar="FILE"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Upload a file to AmoCRM drive."""
    try:
        resource = FilesResource(AmoCRMClient())
        result = resource.upload(file_path)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError, FileNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("download")
def download_file(
    uuid: str = typer.Argument(...),
    output_path: str = typer.Option(..., "--output-path", "-o", help="Path to save the file"),
) -> None:
    """Download a file by UUID."""
    try:
        resource = FilesResource(AmoCRMClient())
        content = resource.download(uuid)
        Path(output_path).write_bytes(content)
        typer.echo(f"File {uuid} saved to {output_path}")
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("delete")
def delete_file(
    uuid: str = typer.Argument(...),
) -> None:
    """Delete a file by UUID."""
    try:
        resource = FilesResource(AmoCRMClient())
        resource.delete(uuid)
        typer.echo(f"File {uuid} deleted.")
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
