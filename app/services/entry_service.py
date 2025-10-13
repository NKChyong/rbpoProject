"""Entry service for reading list management."""

import logging
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Entry, User
from app.domain.schemas import EntryCreate, EntryUpdate

logger = logging.getLogger(__name__)


class EntryService:
    """Service for entry operations."""

    def __init__(self, db: AsyncSession):
        """Initialize entry service."""
        self.db = db

    async def create_entry(self, entry_data: EntryCreate, owner: User) -> Entry:
        """Create a new entry."""
        entry = Entry(
            title=entry_data.title,
            kind=(
                entry_data.kind.value
                if hasattr(entry_data.kind, "value")
                else entry_data.kind
            ),
            link=str(entry_data.link) if entry_data.link else None,
            status=(
                entry_data.status.value
                if hasattr(entry_data.status, "value")
                else entry_data.status
            ),
            description=entry_data.description,
            owner_id=owner.id,
        )

        self.db.add(entry)
        await self.db.flush()
        await self.db.refresh(entry)

        logger.info(f"Entry created: {entry.title} (ID: {entry.id}) by user {owner.id}")
        return entry

    async def get_entry(self, entry_id: int, user: User) -> Entry:
        """Get an entry by ID."""
        result = await self.db.execute(select(Entry).where(Entry.id == entry_id))
        entry = result.scalar_one_or_none()

        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entry not found",
            )

        # Check ownership or admin
        if entry.owner_id != user.id and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this entry",
            )

        return entry

    async def list_entries(
        self,
        user: User,
        status_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Entry], int]:
        """List entries with optional filtering and pagination."""
        # Base query - filter by owner unless admin
        if user.role == "admin":
            query = select(Entry)
            count_query = select(func.count(Entry.id))
        else:
            query = select(Entry).where(Entry.owner_id == user.id)
            count_query = select(func.count(Entry.id)).where(Entry.owner_id == user.id)

        # Apply status filter
        if status_filter:
            query = query.where(Entry.status == status_filter)
            count_query = count_query.where(Entry.status == status_filter)

        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Apply pagination and ordering
        query = query.order_by(Entry.created_at.desc()).limit(limit).offset(offset)

        # Execute query
        result = await self.db.execute(query)
        entries = list(result.scalars().all())

        return entries, total

    async def update_entry(
        self, entry_id: int, entry_data: EntryUpdate, user: User
    ) -> Entry:
        """Update an entry."""
        entry = await self.get_entry(entry_id, user)

        # Update fields if provided
        update_data = entry_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                if field in ["kind", "status"] and hasattr(value, "value"):
                    value = value.value
                if field == "link" and value is not None:
                    value = str(value)
                setattr(entry, field, value)

        await self.db.flush()
        await self.db.refresh(entry)

        logger.info(f"Entry updated: {entry.id} by user {user.id}")
        return entry

    async def delete_entry(self, entry_id: int, user: User) -> None:
        """Delete an entry."""
        entry = await self.get_entry(entry_id, user)

        await self.db.delete(entry)
        await self.db.flush()

        logger.info(f"Entry deleted: {entry_id} by user {user.id}")
