"""AmoCRM CLI — Python library and CLI tool for AmoCRM API v4.

Library usage:
    from amocrm import AmoCRMClient, LeadsResource
    client = AmoCRMClient(subdomain="mycompany", access_token="xxx")
    leads = LeadsResource(client)
    results = leads.list(filters={"pipeline_id": [1]})
"""
from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMAPIError, EntityNotFoundError

# Resource classes added by Wave 5 Agent A after all resources are implemented
# from amocrm.resources import (LeadsResource, ContactsResource, ...)

__all__ = [
    "AmoCRMClient",
    "AmoCRMAPIError",
    "EntityNotFoundError",
]
