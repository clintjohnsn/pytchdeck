"""Test pytchdeck REST API."""

import httpx
from fastapi.testclient import TestClient

from pytchdeck.main import app

client = TestClient(app)


def test_read_root() -> None:
    """Test that reading the root is successful."""
    response = client.get("/pitch", params={"job_description": "hello"})
    assert httpx.codes.is_success(response.status_code)
