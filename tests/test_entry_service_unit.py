"""Unit tests for EntryService covering permission and filtering logic."""

import pytest
from fastapi import HTTPException

from app.core.security import get_password_hash
from app.domain.models import EntryKind, EntryStatus, User, UserRole
from app.domain.schemas import EntryCreate, EntryUpdate, UserCreate
from app.services.entry_service import EntryService
from app.services.user_service import UserService


def _user_payload(email: str, username: str) -> UserCreate:
    """Generate secure user payloads for tests."""
    return UserCreate(email=email, username=username, password="StrongPass!234")


async def _create_admin(db_session) -> User:
    """Create an admin user directly in the database."""
    admin = User(
        email="admin-service@example.com",
        username="service_admin",
        hashed_password=get_password_hash("AdminSecur3!45"),
        role=UserRole.ADMIN.value,
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest.mark.asyncio
async def test_admin_can_list_and_filter_entries(db_session):
    """Admin should see all entries and use status filters."""
    user_service = UserService(db_session)
    owner = await user_service.create_user(_user_payload("owner@example.com", "owner_user"))
    admin = await _create_admin(db_session)

    entry_service = EntryService(db_session)
    owner_entry = await entry_service.create_entry(
        EntryCreate(
            title="Owner entry",
            kind=EntryKind.BOOK,
            status=EntryStatus.TO_READ,
            description="Owner description",
        ),
        owner,
    )
    await entry_service.create_entry(
        EntryCreate(
            title="Admin entry",
            kind=EntryKind.ARTICLE,
            status=EntryStatus.IN_PROGRESS,
        ),
        admin,
    )

    admin_entries, admin_total = await entry_service.list_entries(admin)
    assert admin_total == 2
    assert {entry.owner_id for entry in admin_entries} == {owner_entry.owner_id, admin.id}

    filtered_entries, filtered_total = await entry_service.list_entries(
        admin, status_filter=EntryStatus.IN_PROGRESS.value
    )
    assert filtered_total == 1
    assert filtered_entries[0].status == EntryStatus.IN_PROGRESS.value

    owner_entries, owner_total = await entry_service.list_entries(owner)
    assert owner_total == 1
    assert owner_entries[0].owner_id == owner.id


@pytest.mark.asyncio
async def test_entry_permissions_and_not_found(db_session):
    """Ensure permission checks and 404s are enforced."""
    user_service = UserService(db_session)
    owner = await user_service.create_user(_user_payload("owner2@example.com", "owner_two"))
    other_user = await user_service.create_user(_user_payload("other@example.com", "other_user"))

    entry_service = EntryService(db_session)
    entry = await entry_service.create_entry(
        EntryCreate(
            title="Permissioned entry",
            kind=EntryKind.VIDEO,
            status=EntryStatus.TO_READ,
        ),
        owner,
    )

    with pytest.raises(HTTPException) as exc_forbidden:
        await entry_service.get_entry(entry.id, other_user)
    assert exc_forbidden.value.status_code == 403

    with pytest.raises(HTTPException) as exc_not_found:
        await entry_service.get_entry(9999, owner)
    assert exc_not_found.value.status_code == 404


@pytest.mark.asyncio
async def test_update_and_delete_entry(db_session):
    """Updating and deleting entries should persist changes."""
    user_service = UserService(db_session)
    owner = await user_service.create_user(_user_payload("upd@example.com", "upd_user"))
    entry_service = EntryService(db_session)
    entry = await entry_service.create_entry(
        EntryCreate(
            title="Update me",
            kind=EntryKind.PODCAST,
            status=EntryStatus.IN_PROGRESS,
        ),
        owner,
    )

    updated = await entry_service.update_entry(
        entry.id,
        EntryUpdate(
            status=EntryStatus.COMPLETED,
            description="Finished entry",
        ),
        owner,
    )
    assert updated.status == EntryStatus.COMPLETED.value
    assert updated.description == "Finished entry"

    await entry_service.delete_entry(entry.id, owner)

    with pytest.raises(HTTPException):
        await entry_service.get_entry(entry.id, owner)
