"""Unit tests for user service covering validation branches."""

import pytest
from fastapi import HTTPException

from app.domain.schemas import UserCreate
from app.services.user_service import UserService


def _user_payload(email: str, username: str, password_suffix: str = "A!23456789") -> UserCreate:
    """Helper to build strong passwords for tests."""
    password = f"Strong{password_suffix}"
    return UserCreate(email=email, username=username, password=password)


@pytest.mark.asyncio
async def test_create_user_duplicates_raise(db_session):
    """Creating a user twice should trigger duplicate checks."""
    service = UserService(db_session)
    first = _user_payload("dup@example.com", "dupuser")
    await service.create_user(first)

    with pytest.raises(HTTPException) as exc_email:
        await service.create_user(_user_payload("dup@example.com", "otheruser"))
    assert exc_email.value.status_code == 400
    assert "Email" in exc_email.value.detail

    with pytest.raises(HTTPException) as exc_username:
        await service.create_user(_user_payload("unique@example.com", "dupuser"))
    assert exc_username.value.status_code == 400
    assert "Username" in exc_username.value.detail


@pytest.mark.asyncio
async def test_authenticate_success_and_failures(db_session):
    """Authentication should succeed with correct credentials and fail otherwise."""
    service = UserService(db_session)
    user_data = _user_payload("auth@example.com", "authuser")
    await service.create_user(user_data)

    user = await service.authenticate(user_data.username, user_data.password)
    assert user is not None

    wrong_pass = await service.authenticate(user_data.username, "WrongPass!234")
    missing_user = await service.authenticate("missinguser", user_data.password)

    assert wrong_pass is None
    assert missing_user is None


@pytest.mark.asyncio
async def test_getters_return_expected_user(db_session):
    """Direct getters should fetch users by id, email, and username."""
    service = UserService(db_session)
    payload = _user_payload("getters@example.com", "getteruser")
    created = await service.create_user(payload)

    by_id = await service.get_by_id(created.id)
    by_email = await service.get_by_email(payload.email)
    by_username = await service.get_by_username(payload.username)

    assert by_id is not None and by_id.id == created.id
    assert by_email is not None and by_email.email == payload.email
    assert by_username is not None and by_username.username == payload.username
