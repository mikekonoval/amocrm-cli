# amocrm/resources/loss_reasons.py
"""LossReasonsResource for AmoCRM API v4."""
from __future__ import annotations

from amocrm.resources.base import BaseResource

__all__ = ["LossReasonsResource"]


class LossReasonsResource(BaseResource):
    path = "/leads/loss_reasons"
    embedded_key = "loss_reasons"
