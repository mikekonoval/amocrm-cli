"""CLI commands for account resource."""
from __future__ import annotations

from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError
from amocrm.resources.account import AccountResource

app = typer.Typer(name="account", help="Manage account")


@app.command("info")
def info(
    with_: Optional[str] = typer.Option(None, "--with", help="Comma-separated extra data to include"),
    output: str = typer.Option("table", "--output"),
) -> None:
    try:
        resource = AccountResource(AmoCRMClient())
        with_list = with_.split(",") if with_ else None
        result = resource.get(with_=with_list)
        render(result, output=output)
    except AmoCRMAPIError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
