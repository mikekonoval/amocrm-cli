"""AmoCRM CLI root application."""
import typer

app = typer.Typer(
    name="amocrm",
    help="AmoCRM API CLI tool",
    no_args_is_help=True,
)

# Command groups registered here by Wave 5 Agent A
# Example: app.add_typer(leads_app, name="leads")

if __name__ == "__main__":
    app()
