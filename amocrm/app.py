"""AmoCRM CLI root application."""
import typer

from amocrm.commands.leads import app as leads_app
from amocrm.commands.contacts import app as contacts_app
from amocrm.commands.companies import app as companies_app
from amocrm.commands.tasks import app as tasks_app
from amocrm.commands.notes import app as notes_app
from amocrm.commands.pipelines import app as pipelines_app
from amocrm.commands.users import app as users_app
from amocrm.commands.tags import app as tags_app
from amocrm.commands.custom_fields import app as custom_fields_app
from amocrm.commands.catalogs import app as catalogs_app
from amocrm.commands.events import app as events_app
from amocrm.commands.webhooks import app as webhooks_app
from amocrm.commands.account import app as account_app
from amocrm.commands.auth import app as auth_app
from amocrm.commands.loss_reasons import app as loss_reasons_app
from amocrm.commands.calls import app as calls_app
from amocrm.commands.unsorted import app as unsorted_app
from amocrm.commands.files import app as files_app
from amocrm.commands.chats import app as chats_app

app = typer.Typer(
    name="amocrm",
    help="AmoCRM API CLI tool",
    no_args_is_help=True,
)

app.add_typer(leads_app, name="leads")
app.add_typer(contacts_app, name="contacts")
app.add_typer(companies_app, name="companies")
app.add_typer(tasks_app, name="tasks")
app.add_typer(notes_app, name="notes")
app.add_typer(pipelines_app, name="pipelines")
app.add_typer(users_app, name="users")
app.add_typer(tags_app, name="tags")
app.add_typer(custom_fields_app, name="custom-fields")
app.add_typer(catalogs_app, name="catalogs")
app.add_typer(events_app, name="events")
app.add_typer(webhooks_app, name="webhooks")
app.add_typer(account_app, name="account")
app.add_typer(auth_app, name="auth")
app.add_typer(loss_reasons_app, name="loss-reasons")
app.add_typer(calls_app, name="calls")
app.add_typer(unsorted_app, name="unsorted")
app.add_typer(files_app, name="files")
app.add_typer(chats_app, name="chats")

if __name__ == "__main__":
    app()
