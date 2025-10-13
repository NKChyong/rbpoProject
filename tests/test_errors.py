"""Tests for error handling and validation."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_not_found_entry(client: AsyncClient, test_user: dict):
    """Test 404 error for non-existent entry."""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    response = await client.get("/api/v1/entries/99999", headers=headers)

    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] in ["not_found", "http_error"]


@pytest.mark.asyncio
async def test_validation_error_missing_fields(client: AsyncClient, test_user: dict):
    """Test validation error for missing required fields."""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    # Missing required 'kind' field
    entry_data = {"title": "Test Entry"}

    response = await client.post("/api/v1/entries", json=entry_data, headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_validation_error_invalid_enum(client: AsyncClient, test_user: dict):
    """Test validation error for invalid enum value."""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    entry_data = {
        "title": "Test Entry",
        "kind": "invalid_kind",  # Invalid enum value
        "status": "to_read",
    }

    response = await client.post("/api/v1/entries", json=entry_data, headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test 403 error for unauthorized access."""
    # No Authorization header
    response = await client.get("/api/v1/entries")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_invalid_token(client: AsyncClient):
    """Test 401 error for invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = await client.get("/api/v1/entries", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_validation_error_title_too_long(client: AsyncClient, test_user: dict):
    """Test validation error for title exceeding max length."""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    entry_data = {"title": "x" * 501, "kind": "book", "status": "to_read"}  # Max is 500

    response = await client.post("/api/v1/entries", json=entry_data, headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_validation_error_invalid_status_filter(client: AsyncClient, test_user: dict):
    """Test validation error for invalid status filter."""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    response = await client.get("/api/v1/entries?status=invalid_status", headers=headers)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_error_response_structure(client: AsyncClient):
    """Test that error responses follow the correct structure."""
    response = await client.get("/api/v1/entries/99999")

    assert response.status_code in [401, 403, 404]
    data = response.json()

    # Check error structure
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
