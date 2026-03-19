# amocrm/commands/calls.py
"""CLI commands for calls resource."""
from __future__ import annotations

from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.calls import CallsResource

app = typer.Typer(name="calls", help="Log calls", no_args_is_help=True)


@app.callback()
def _callback() -> None:
    """Log calls."""


@app.command("add")
def add_call(
    direction: str = typer.Option(..., "--direction", help="inbound or outbound"),
    duration: int = typer.Option(..., "--duration", help="Duration in seconds"),
    source: str = typer.Option(..., "--source", help="Call source name"),
    phone: str = typer.Option(..., "--phone", help="Phone number"),
    call_status: int = typer.Option(..., "--call-status", help="1=no answer, 2=busy, 3=rejected, 4=answered, 5=unknown, 6=voicemail"),
    responsible_user_id: int = typer.Option(..., "--responsible-user-id"),
    link: Optional[str] = typer.Option(None, "--link", help="Recording URL"),
    call_result: Optional[str] = typer.Option(None, "--call-result"),
    created_at: Optional[int] = typer.Option(None, "--created-at", help="Unix timestamp"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Log a call."""
    try:
        data: dict[str, object] = {
            "direction": direction,
            "duration": duration,
            "source": source,
            "phone": phone,
            "call_status": call_status,
            "responsible_user_id": responsible_user_id,
        }
        if link is not None:
            data["link"] = link
        if call_result is not None:
            data["call_result"] = call_result
        if created_at is not None:
            data["created_at"] = created_at
        resource = CallsResource(AmoCRMClient())
        results = resource.add([data])
        render(results, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
