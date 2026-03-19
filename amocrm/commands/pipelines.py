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


@app.command("create")
def create_pipeline(
    name: str = typer.Option(..., "--name"),
    sort: int = typer.Option(100, "--sort"),
    is_unsorted_on: bool = typer.Option(False, "--is-unsorted-on"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Create a new pipeline (includes a default first stage)."""
    try:
        resource = PipelinesResource(AmoCRMClient())
        results = resource.create([{
            "name": name,
            "sort": sort,
            "is_main": False,
            "is_unsorted_on": is_unsorted_on,
            "_embedded": {
                "statuses": [
                    {"name": "Новый", "sort": 10, "color": "#fffeb2"},
                ]
            },
        }])
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("delete")
def delete_pipeline(
    id: int = typer.Argument(...),
) -> None:
    """Delete a pipeline by ID."""
    try:
        resource = PipelinesResource(AmoCRMClient())
        resource.delete(id)
        typer.echo(f"Pipeline {id} deleted.")
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@stages_app.command("create")
def create_stage(
    pipeline_id: int = typer.Argument(...),
    name: str = typer.Option(..., "--name"),
    sort: int = typer.Option(10, "--sort"),
    color: str = typer.Option("#fffeb2", "--color"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Create a stage in a pipeline."""
    try:
        resource = StagesResource(AmoCRMClient(), pipeline_id=pipeline_id)
        results = resource.create([{"name": name, "sort": sort, "color": color}])
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@stages_app.command("update")
def update_stage(
    pipeline_id: int = typer.Argument(...),
    stage_id: int = typer.Argument(...),
    name: Optional[str] = typer.Option(None, "--name"),
    sort: Optional[int] = typer.Option(None, "--sort"),
    color: Optional[str] = typer.Option(None, "--color"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Update a stage in a pipeline."""
    try:
        data: dict[str, object] = {}
        if name is not None:
            data["name"] = name
        if sort is not None:
            data["sort"] = sort
        if color is not None:
            data["color"] = color
        if not data:
            typer.echo("Provide at least one field to update.", err=True)
            raise typer.Exit(1)
        resource = StagesResource(AmoCRMClient(), pipeline_id=pipeline_id)
        result = resource.update(stage_id, data)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@stages_app.command("delete")
def delete_stage(
    pipeline_id: int = typer.Argument(...),
    stage_id: int = typer.Argument(...),
) -> None:
    """Delete a stage from a pipeline."""
    try:
        resource = StagesResource(AmoCRMClient(), pipeline_id=pipeline_id)
        resource.delete(stage_id)
        typer.echo(f"Stage {stage_id} deleted.")
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
