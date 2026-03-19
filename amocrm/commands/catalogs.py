"""CLI commands for catalogs resource."""
from __future__ import annotations

from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.catalogs import CatalogsResource, CatalogElementsResource

app = typer.Typer(name="catalogs", help="Manage catalogs")
elements_app = typer.Typer(name="elements", help="Manage catalog elements")


def _get_catalogs_resource() -> CatalogsResource:
    return CatalogsResource(AmoCRMClient())


def _get_elements_resource(catalog_id: int) -> CatalogElementsResource:
    return CatalogElementsResource(AmoCRMClient(), catalog_id=catalog_id)


# Catalog commands
@app.command("list")
def list_catalogs(
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(50, "--limit"),
    output: str = typer.Option("table", "--output"),
    columns: Optional[str] = typer.Option(None, "--columns"),
) -> None:
    """List catalogs."""
    try:
        cols = columns.split(",") if columns else None
        resource = _get_catalogs_resource()
        results = resource.list(page=page, limit=limit)
        render(results, output=output, columns=cols)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("get")
def get_catalog(
    id: int = typer.Argument(...),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Get a catalog by ID."""
    try:
        resource = _get_catalogs_resource()
        result = resource.get(id)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("create")
def create_catalog(
    name: str = typer.Option(..., "--name"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Create a new catalog."""
    try:
        data = {"name": name}
        resource = _get_catalogs_resource()
        results = resource.create([data])
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("delete")
def delete_catalog(
    id: int = typer.Argument(...),
) -> None:
    """Delete a catalog by ID."""
    try:
        resource = _get_catalogs_resource()
        resource.delete(id)
        typer.echo(f"Catalog {id} deleted.")
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


# Elements sub-commands
@elements_app.command("list")
def list_elements(
    catalog_id: int = typer.Argument(...),
    page: int = typer.Option(1, "--page"),
    limit: int = typer.Option(50, "--limit"),
    output: str = typer.Option("table", "--output"),
    columns: Optional[str] = typer.Option(None, "--columns"),
) -> None:
    """List elements in a catalog."""
    try:
        cols = columns.split(",") if columns else None
        resource = _get_elements_resource(catalog_id)
        results = resource.list(page=page, limit=limit)
        render(results, output=output, columns=cols)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@elements_app.command("get")
def get_element(
    catalog_id: int = typer.Argument(...),
    id: int = typer.Argument(...),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Get an element by ID."""
    try:
        resource = _get_elements_resource(catalog_id)
        result = resource.get(id)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@elements_app.command("create")
def create_element(
    catalog_id: int = typer.Argument(...),
    name: str = typer.Option(..., "--name"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Create a new element in a catalog."""
    try:
        data = {"name": name}
        resource = _get_elements_resource(catalog_id)
        results = resource.create([data])
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@elements_app.command("delete")
def delete_element(
    catalog_id: int = typer.Argument(...),
    id: int = typer.Argument(...),
) -> None:
    """Delete an element by ID."""
    try:
        resource = _get_elements_resource(catalog_id)
        resource.delete(id)
        typer.echo(f"Element {id} deleted.")
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


# Add elements sub-app to main app
app.add_typer(elements_app)
