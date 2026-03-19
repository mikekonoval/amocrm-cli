from amocrm.resources.leads import LeadsResource
from amocrm.resources.contacts import ContactsResource
from amocrm.resources.companies import CompaniesResource
from amocrm.resources.tasks import TasksResource
from amocrm.resources.notes import NotesResource
from amocrm.resources.pipelines import PipelinesResource, StagesResource
from amocrm.resources.users import UsersResource, RolesResource
from amocrm.resources.tags import TagsResource
from amocrm.resources.custom_fields import CustomFieldsResource, CustomFieldGroupsResource
from amocrm.resources.catalogs import CatalogsResource, CatalogElementsResource
from amocrm.resources.events import EventsResource
from amocrm.resources.webhooks import WebhooksResource
from amocrm.resources.account import AccountResource

__all__ = [
    "LeadsResource",
    "ContactsResource",
    "CompaniesResource",
    "TasksResource",
    "NotesResource",
    "PipelinesResource",
    "StagesResource",
    "UsersResource",
    "RolesResource",
    "TagsResource",
    "CustomFieldsResource",
    "CustomFieldGroupsResource",
    "CatalogsResource",
    "CatalogElementsResource",
    "EventsResource",
    "WebhooksResource",
    "AccountResource",
]
