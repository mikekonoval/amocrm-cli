"""CLI commands for webhooks resource."""
from __future__ import annotations

from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.webhooks import WebhooksResource

app = typer.Typer(name="webhooks", help="Manage webhooks")


def _get_resource() -> WebhooksResource:
    return WebhooksResource(AmoCRMClient())


@app.command("list")
def list_webhooks(
    output: str = typer.Option("table", "--output"),
    columns: Optional[str] = typer.Option(None, "--columns"),
) -> None:
    """List all registered webhooks."""
    try:
        cols = columns.split(",") if columns else None
        resource = _get_resource()
        results = resource.list()
        render(results, output=output, columns=cols)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("subscribe")
def subscribe_webhook(
    url: str = typer.Option(..., "--url", help="Destination URL for the webhook"),
    events: str = typer.Option(..., "--events", help="Comma-separated list of events, e.g. leads_add,task_add"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Subscribe a webhook to receive events."""
    try:
        settings = [e.strip() for e in events.split(",") if e.strip()]
        resource = _get_resource()
        result = resource.subscribe(url, settings)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("unsubscribe")
def unsubscribe_webhook(
    url: str = typer.Option(..., "--url", help="Destination URL of the webhook to remove"),
) -> None:
    """Unsubscribe (delete) a webhook by its destination URL."""
    try:
        resource = _get_resource()
        resource.unsubscribe(url)
        typer.echo(f"Webhook {url!r} removed.")
    except EntityNotFoundError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
    except AmoCRMAPIError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
