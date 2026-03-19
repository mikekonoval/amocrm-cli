"""CompaniesResource for AmoCRM API v4."""
from __future__ import annotations

from amocrm.resources.base import BaseResource

__all__ = ["CompaniesResource"]


class CompaniesResource(BaseResource):
    path = "/companies"
    embedded_key = "companies"
