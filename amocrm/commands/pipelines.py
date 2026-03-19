"""CLI commands for pipelines and stages."""
from __future__ import annotations

from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.pipelines import PipelinesResource, StagesResource

app = typer.Typer(name="pipelines", help="Manage pipelines and stages")
stages_app = typer.Typer(name="stages", help="Manage pipeline stages")
app.add_typer(stages_app, name="stages")


@app.command("list")
def list_pipelines(
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(50, "--limit"),
    output: str = typer.Option("table", "--output"),
    columns: Optional[str] = typer.Option(None, "--columns"),
) -> None:
    """List pipelines."""
    try:
        resource = PipelinesResource(AmoCRMClient())
        results = resource.list(page=page, limit=limit)
        render(results, output=output, columns=columns.split(",") if columns else None)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("get")
def get_pipeline(
    id: int = typer.Argument(...),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Get a pipeline by ID."""
    try:
        resource = PipelinesResource(AmoCRMClient())
        result = resource.get(id)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@stages_app.command("list")
def list_stages(
    pipeline_id: int = typer.Argument(...),
    output: str = typer.Option("table", "--output"),
    columns: Optional[str] = typer.Option(None, "--columns"),
) -> None:
    """List stages for a pipeline."""
    try:
        resource = StagesResource(AmoCRMClient(), pipeline_id=pipeline_id)
        results = resource.list()
        render(results, output=output, columns=columns.split(",") if columns else None)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@stages_app.command("get")
def get_stage(
    pipeline_id: int = typer.Argument(...),
    stage_id: int = typer.Argument(...),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Get a stage by ID within a pipeline."""
    try:
        resource = StagesResource(AmoCRMClient(), pipeline_id=pipeline_id)
        result = resource.get(stage_id)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
