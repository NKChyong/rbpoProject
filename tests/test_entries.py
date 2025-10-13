"""Tests for entry endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_entry(client: AsyncClient, test_user: dict):
    """Test creating an entry."""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    entry_data = {
        "title": "Clean Code",
        "kind": "book",
        "link": "https://example.com/clean-code",
        "status": "to_read",
        "description": "A book about writing clean code",
    }

    response = await client.post("/api/v1/entries", json=entry_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == entry_data["title"]
    assert data["kind"] == entry_data["kind"]
    assert data["status"] == entry_data["status"]
    assert data["owner_id"] == test_user["user"]["id"]


@pytest.mark.asyncio
async def test_create_entry_unauthorized(client: AsyncClient):
    """Test creating entry without authentication."""
    entry_data = {
        "title": "Clean Code",
        "kind": "book",
        "status": "to_read",
    }

    response = await client.post("/api/v1/entries", json=entry_data)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_entry_invalid_kind(client: AsyncClient, test_user: dict):
    """Test creating entry with invalid kind."""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    entry_data = {
        "title": "Test Entry",
        "kind": "invalid_kind",
        "status": "to_read",
    }

    response = await client.post("/api/v1/entries", json=entry_data, headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_entry_invalid_status(client: AsyncClient, test_user: dict):
    """Test creating entry with invalid status."""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    entry_data = {
        "title": "Test Entry",
        "kind": "book",
        "status": "invalid_status",
    }

    response = await client.post("/api/v1/entries", json=entry_data, headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_entries(client: AsyncClient, test_user: dict):
    """Test listing entries."""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}

    # Create some entries
    for i in range(3):
        entry_data = {
            "title": f"Entry {i}",
            "kind": "article",
            "status": "to_read",
        }
        await client.post("/api/v1/entries", json=entry_data, headers=headers)

    # List entries
    response = await client.get("/api/v1/entries", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_list_entries_with_status_filter(client: AsyncClient, test_user: dict):
    """Test listing entries with status filter."""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}

    # Create entries with different statuses
    await client.post(
        "/api/v1/entries",
        json={"title": "Entry 1", "kind": "book", "status": "to_read"},
        headers=headers,
    )
    await client.post(
        "/api/v1/entries",
        json={"title": "Entry 2", "kind": "article", "status": "in_progress"},
        headers=headers,
    )
    await client.post(
        "/api/v1/entries",
        json={"title": "Entry 3", "kind": "video", "status": "completed"},
        headers=headers,
    )

    # Filter by status
    response = await client.get("/api/v1/entries?status=to_read", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["status"] == "to_read"


@pytest.mark.asyncio
async def test_list_entries_pagination(client: AsyncClient, test_user: dict):
    """Test entries pagination."""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}

    # Create 5 entries
    for i in range(5):
        await client.post(
            "/api/v1/entries",
            json={"title": f"Entry {i}", "kind": "article", "status": "to_read"},
            headers=headers,
        )

    # Get first page
    response = await client.get("/api/v1/entries?limit=2&offset=0", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2

    # Get second page
    response = await client.get("/api/v1/entries?limit=2&offset=2", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_get_entry(client: AsyncClient, test_user: dict):
    """Test getting a specific entry."""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}

    # Create entry
    entry_data = {"title": "Test Entry", "kind": "book", "status": "to_read"}
    create_response = await client.post("/api/v1/entries", json=entry_data, headers=headers)
    entry_id = create_response.json()["id"]

    # Get entry
    response = await client.get(f"/api/v1/entries/{entry_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == entry_id
    assert data["title"] == entry_data["title"]


@pytest.mark.asyncio
async def test_get_entry_not_found(client: AsyncClient, test_user: dict):
    """Test getting nonexistent entry."""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}

    response = await client.get("/api/v1/entries/99999", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_entry_forbidden(client: AsyncClient, test_user: dict):
    """Test accessing another user's entry."""
    # Create first user and entry
    headers1 = {"Authorization": f"Bearer {test_user['access_token']}"}
    entry_data = {"title": "User 1 Entry", "kind": "book", "status": "to_read"}
    create_response = await client.post("/api/v1/entries", json=entry_data, headers=headers1)
    entry_id = create_response.json()["id"]

    # Create second user
    user2_data = {
        "email": "user2@example.com",
        "username": "user2",
        "password": "password123",
    }
    await client.post("/api/v1/auth/register", json=user2_data)
    login_response = await client.post(
        "/api/v1/auth/login", json={"username": "user2", "password": "password123"}
    )
    user2_token = login_response.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {user2_token}"}

    # Try to access first user's entry
    response = await client.get(f"/api/v1/entries/{entry_id}", headers=headers2)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_entry(client: AsyncClient, test_user: dict):
    """Test updating an entry."""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}

    # Create entry
    entry_data = {"title": "Original Title", "kind": "book", "status": "to_read"}
    create_response = await client.post("/api/v1/entries", json=entry_data, headers=headers)
    entry_id = create_response.json()["id"]

    # Update entry
    update_data = {"title": "Updated Title", "status": "in_progress"}
    response = await client.patch(f"/api/v1/entries/{entry_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["status"] == update_data["status"]
    assert data["kind"] == entry_data["kind"]  # Unchanged


@pytest.mark.asyncio
async def test_delete_entry(client: AsyncClient, test_user: dict):
    """Test deleting an entry."""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}

    # Create entry
    entry_data = {"title": "Entry to Delete", "kind": "article", "status": "to_read"}
    create_response = await client.post("/api/v1/entries", json=entry_data, headers=headers)
    entry_id = create_response.json()["id"]

    # Delete entry
    response = await client.delete(f"/api/v1/entries/{entry_id}", headers=headers)
    assert response.status_code == 204

    # Verify entry is deleted
    get_response = await client.get(f"/api/v1/entries/{entry_id}", headers=headers)
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_admin_can_access_all_entries(client: AsyncClient, test_user: dict, admin_user: dict):
    """Test that admin can access all entries."""
    # Create entry as regular user
    user_headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    entry_data = {"title": "User Entry", "kind": "book", "status": "to_read"}
    create_response = await client.post("/api/v1/entries", json=entry_data, headers=user_headers)
    entry_id = create_response.json()["id"]

    # Access as admin
    admin_headers = {"Authorization": f"Bearer {admin_user['access_token']}"}
    response = await client.get(f"/api/v1/entries/{entry_id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["id"] == entry_id
