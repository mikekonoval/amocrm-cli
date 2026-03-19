"""CLI commands for auth management."""
from __future__ import annotations

import datetime
from typing import Optional

import typer

from amocrm.auth.config import CONFIG_PATH, load_config, save_config
from amocrm.auth.oauth import run_browser_flow
from amocrm.auth.token import make_longtoken_config

app = typer.Typer(name="auth", help="Manage AmoCRM authentication")


@app.command("login")
def login(
    subdomain: str = typer.Option(..., "--subdomain", help="AmoCRM subdomain (e.g. mycompany)"),
    token: Optional[str] = typer.Option(None, "--token", help="Long-lived access token"),
    oauth: bool = typer.Option(False, "--oauth", help="Use OAuth 2.0 browser flow"),
    client_id: Optional[str] = typer.Option(None, "--client-id", help="OAuth client ID"),
    client_secret: Optional[str] = typer.Option(None, "--client-secret", help="OAuth client secret"),
    redirect_uri: str = typer.Option("http://localhost:8080", "--redirect-uri"),
) -> None:
    """Authenticate with AmoCRM (long-lived token or OAuth)."""
    if oauth:
        if not client_id:
            typer.echo("--client-id is required for --oauth", err=True)
            raise typer.Exit(1)
        if not client_secret:
            typer.echo("--client-secret is required for --oauth", err=True)
            raise typer.Exit(1)
        try:
            tokens = run_browser_flow(
                subdomain=subdomain,
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
            )
        except Exception as e:
            typer.echo(str(e), err=True)
            raise typer.Exit(1)
        config: dict[str, object] = {
            "subdomain": subdomain,
            "auth_mode": "oauth",
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "expires_at": tokens["expires_at"],
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
        }
        save_config(config)
        typer.echo(f"Logged in to {subdomain} via OAuth.")
    elif token:
        config = make_longtoken_config(subdomain, token)
        save_config(config)
        typer.echo(f"Logged in to {subdomain} with long-lived token.")
    else:
        typer.echo("Provide --token <token> or --oauth", err=True)
        raise typer.Exit(1)


@app.command("status")
def status() -> None:
    """Show current authentication status."""
    try:
        config = load_config()
    except FileNotFoundError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1)

    subdomain = config.get("subdomain", "unknown")
    auth_mode = config.get("auth_mode", "unknown")
    typer.echo(f"Subdomain : {subdomain}")
    typer.echo(f"Auth mode : {auth_mode}")

    expires_at = config.get("expires_at")
    if expires_at is not None and isinstance(expires_at, (int, float)):
        dt = datetime.datetime.fromtimestamp(int(expires_at))
        typer.echo(f"Token expires: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        typer.echo("Token expires: never (long-lived token)")


@app.command("logout")
def logout() -> None:
    """Remove stored credentials."""
    if CONFIG_PATH.exists():
        CONFIG_PATH.unlink()
        typer.echo("Logged out. Config removed.")
    else:
        typer.echo("No config found; already logged out.")
