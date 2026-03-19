"""Shared test fixtures. Add ONLY base fixtures here.
Resource-specific sample data belongs in each test file.
"""
import pytest
import typer.testing
from amocrm.client import AmoCRMClient


@pytest.fixture
def mock_config() -> dict:
    return {
        "subdomain": "testcompany",
        "auth_mode": "longtoken",
        "access_token": "test-access-token",
        "refresh_token": None,
        "expires_at": None,
        "client_id": None,
        "client_secret": None,
        "redirect_uri": "http://localhost:8080",
    }


@pytest.fixture
def mock_client() -> AmoCRMClient:
    return AmoCRMClient(subdomain="testcompany", access_token="test-access-token")


@pytest.fixture
def cli_runner() -> typer.testing.CliRunner:
    return typer.testing.CliRunner()
