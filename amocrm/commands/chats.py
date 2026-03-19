"""CLI commands for the AmoCRM Chats (amojo) API."""
from __future__ import annotations

from typing import Optional

import typer

from amocrm.client import AmoCRMClient
from amocrm.commands.output import render
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError
from amocrm.resources.chats import ChatsResource

app = typer.Typer(name="chats", help="Manage chats via amojo API")


def _get_resource() -> ChatsResource:
    return ChatsResource(AmoCRMClient())


@app.command("connect")
def connect(
    account_chat_id: str = typer.Argument(..., help="amojo_id from GET /api/v4/account?with=amojo_id"),
    title: str = typer.Option(..., "--title", help="Display name for this chat channel"),
    hook_url: str = typer.Option(..., "--hook-url", help="Webhook URL to receive incoming messages"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Connect (register) a chat channel with AmoCRM."""
    try:
        resource = _get_resource()
        result = resource.connect(account_chat_id=account_chat_id, title=title, hook_url=hook_url)
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("disconnect")
def disconnect(
    account_chat_id: str = typer.Argument(...),
) -> None:
    """Disconnect the chat channel."""
    try:
        resource = _get_resource()
        resource.disconnect(account_chat_id=account_chat_id)
        typer.echo(f"Chat channel {account_chat_id} disconnected.")
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("create")
def create_chat(
    account_chat_id: str = typer.Argument(...),
    source_uid: str = typer.Option(..., "--source-uid", help="Unique ID from your chat system"),
    contact_id: Optional[int] = typer.Option(None, "--contact-id", help="Link to AmoCRM contact"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Create a new chat conversation."""
    try:
        resource = _get_resource()
        result = resource.create_chat(
            account_chat_id=account_chat_id,
            source_uid=source_uid,
            contact_id=contact_id,
        )
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)


@app.command("send")
def send_message(
    account_chat_id: str = typer.Argument(...),
    chat_id: str = typer.Argument(...),
    text: str = typer.Option(..., "--text"),
    sender_id: str = typer.Option(..., "--sender-id"),
    sender_name: str = typer.Option(..., "--sender-name"),
    output: str = typer.Option("table", "--output"),
) -> None:
    """Send a message in a chat conversation."""
    try:
        resource = _get_resource()
        result = resource.send_message(
            account_chat_id=account_chat_id,
            chat_id=chat_id,
            text=text,
            sender_id=sender_id,
            sender_name=sender_name,
        )
        render(result, output=output)
    except (AmoCRMAPIError, EntityNotFoundError) as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)
