"""Entry endpoints for reading list management."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.database import get_db
from app.core.config import settings
from app.core.security import get_current_active_user
from app.domain.models import EntryStatus, User
from app.domain.schemas import EntryCreate, EntryListResponse, EntryResponse, EntryUpdate
from app.services.entry_service import EntryService

router = APIRouter(prefix="/entries", tags=["entries"])
logger = logging.getLogger(__name__)


@router.post("", response_model=EntryResponse, status_code=status.HTTP_201_CREATED)
async def create_entry(
    entry_data: EntryCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> EntryResponse:
    """
    Create a new reading list entry.

    - **title**: Entry title (1-500 characters)
    - **kind**: Type of content (book, article, video, podcast, other)
    - **link**: Optional URL to the content
    - **status**: Current status (to_read, in_progress, completed, archived)
    - **description**: Optional description
    """
    entry_service = EntryService(db)
    entry = await entry_service.create_entry(entry_data, current_user)
    return EntryResponse.model_validate(entry)


@router.get("", response_model=EntryListResponse)
async def list_entries(
    status: Optional[str] = Query(
        None, description="Filter by status (to_read, in_progress, completed, archived)"
    ),
    limit: int = Query(
        settings.default_limit,
        ge=1,
        le=settings.max_limit,
        description="Number of items to return",
    ),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> EntryListResponse:
    """
    List reading list entries with optional filtering and pagination.

    - **status**: Optional filter by status
    - **limit**: Number of items to return (default: 50, max: 100)
    - **offset**: Number of items to skip (default: 0)

    Returns entries owned by the current user (or all entries for admins).
    """
    # Validate status if provided
    if status and status not in [s.value for s in EntryStatus]:
        valid_statuses = [s.value for s in EntryStatus]
        logger.warning(f"Invalid status filter: {status}")
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}",
        )

    entry_service = EntryService(db)
    entries, total = await entry_service.list_entries(
        current_user, status, limit, offset
    )

    return EntryListResponse(
        items=[EntryResponse.model_validate(entry) for entry in entries],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{entry_id}", response_model=EntryResponse)
async def get_entry(
    entry_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> EntryResponse:
    """
    Get a specific entry by ID.

    Only the owner or an admin can access the entry.
    """
    entry_service = EntryService(db)
    entry = await entry_service.get_entry(entry_id, current_user)
    return EntryResponse.model_validate(entry)


@router.patch("/{entry_id}", response_model=EntryResponse)
async def update_entry(
    entry_id: int,
    entry_data: EntryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> EntryResponse:
    """
    Update an entry.

    Only the owner or an admin can update the entry.
    All fields are optional - only provided fields will be updated.
    """
    entry_service = EntryService(db)
    entry = await entry_service.update_entry(entry_id, entry_data, current_user)
    return EntryResponse.model_validate(entry)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(
    entry_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete an entry.

    Only the owner or an admin can delete the entry.
    """
    entry_service = EntryService(db)
    await entry_service.delete_entry(entry_id, current_user)
    return None
