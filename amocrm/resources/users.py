"""UsersResource and RolesResource for AmoCRM API v4."""
from __future__ import annotations

from amocrm.resources.base import BaseResource

__all__ = ["UsersResource", "RolesResource"]


class UsersResource(BaseResource):
    path = "/users"
    embedded_key = "users"


class RolesResource(BaseResource):
    path = "/roles"
    embedded_key = "roles"
