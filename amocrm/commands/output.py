"""Render data as table, json, or csv."""
from __future__ import annotations

import csv
import json
import sys

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def render(
    data: list[dict] | dict,
    output: str = "table",
    columns: list[str] | None = None,
) -> None:
    if isinstance(data, dict):
        data = [data]
    if not data:
        typer.echo("(no results)")
        return
    if output == "json":
        typer.echo(json.dumps(data, indent=2, ensure_ascii=False))
    elif output == "csv":
        cols = columns or list(data[0].keys())
        writer = csv.DictWriter(sys.stdout, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)
    else:  # table
        cols = columns or list(data[0].keys())
        table = Table(*cols)
        for row in data:
            table.add_row(*[str(row.get(c, "")) for c in cols])
        console.print(table)
