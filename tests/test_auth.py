"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration."""
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "StrongPass!234",
    }

    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user: dict):
    """Test registration with duplicate email."""
    user_data = {
        "email": test_user["user"]["email"],
        "username": "anotheruser",
        "password": "AnotherStr0ng!45",
    }

    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    data = response.json()
    assert "email" in data["error"]["message"].lower()


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient, test_user: dict):
    """Test registration with duplicate username."""
    user_data = {
        "email": "another@example.com",
        "username": test_user["user"]["username"],
        "password": "AnotherStr0ng!45",
    }

    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    data = response.json()
    assert "username" in data["error"]["message"].lower()


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: dict):
    """Test successful login."""
    # test_user fixture already creates and logs in, so we just verify
    assert "access_token" in test_user
    assert "refresh_token" in test_user


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, test_user: dict):
    """Test login with invalid credentials."""
    login_data = {
        "username": test_user["user"]["username"],
        "password": "wrongpassword",
    }

    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with nonexistent user."""
    login_data = {"username": "nonexistent", "password": "StrongPass!234"}

    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_user_weak_password(client: AsyncClient):
    """Weak passwords should be rejected."""
    user_data = {
        "email": "weak@example.com",
        "username": "weakuser",
        "password": "password123",  # lacks complexity and length
    }

    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, test_user: dict):
    """Test token refresh."""
    refresh_data = {"refresh_token": test_user["refresh_token"]}

    response = await client.post("/api/v1/auth/refresh", json=refresh_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    """Test refresh with invalid token."""
    refresh_data = {"refresh_token": "invalid_token"}

    response = await client.post("/api/v1/auth/refresh", json=refresh_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, test_user: dict):
    """Test logout endpoint."""
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}

    response = await client.post("/api/v1/auth/logout", headers=headers)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_login_inactive_user(client: AsyncClient, db_session):
    """Inactive users should receive 403 during login."""
    user_data = {
        "email": "inactive@example.com",
        "username": "inactive_user",
        "password": "StrongPass!234",
    }
    await client.post("/api/v1/auth/register", json=user_data)

    from app.services.user_service import UserService

    user_service = UserService(db_session)
    user = await user_service.get_by_username(user_data["username"])
    user.is_active = False
    await db_session.commit()

    response = await client.post("/api/v1/auth/login", json=user_data)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_refresh_with_access_token_fails(client: AsyncClient, test_user: dict):
    """Using an access token in refresh endpoint should fail."""
    access_token = test_user["access_token"]
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_for_inactive_user(client: AsyncClient, db_session, test_user: dict):
    """Refresh should fail if user becomes inactive."""
    refresh_token = test_user["refresh_token"]

    from app.services.user_service import UserService

    user_service = UserService(db_session)
    user = await user_service.get_by_username(test_user["user"]["username"])
    user.is_active = False
    await db_session.commit()

    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 401
