"""Pydantic schemas for API request/response models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.domain.models import EntryKind, EntryStatus, UserRole


# Error schemas
class ErrorDetail(BaseModel):
    """Error detail schema."""

    code: str
    message: str
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: ErrorDetail


# User schemas
class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str = Field(min_length=3, max_length=100)


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(min_length=8, max_length=100)


class UserResponse(UserBase):
    """User response schema."""

    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Auth schemas
class LoginRequest(BaseModel):
    """Login request schema."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str


# Entry schemas
class EntryBase(BaseModel):
    """Base entry schema."""

    title: str = Field(min_length=1, max_length=500)
    kind: EntryKind
    link: Optional[str] = None
    status: EntryStatus = EntryStatus.TO_READ
    description: Optional[str] = Field(None, max_length=5000)

    @field_validator("kind")
    @classmethod
    def validate_kind(cls, v: EntryKind) -> str:
        """Validate entry kind."""
        if isinstance(v, EntryKind):
            return v.value
        if v not in [k.value for k in EntryKind]:
            raise ValueError(
                f"Invalid kind. Must be one of: {[k.value for k in EntryKind]}"
            )
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: EntryStatus) -> str:
        """Validate entry status."""
        if isinstance(v, EntryStatus):
            return v.value
        if v not in [s.value for s in EntryStatus]:
            raise ValueError(
                f"Invalid status. Must be one of: {[s.value for s in EntryStatus]}"
            )
        return v


class EntryCreate(EntryBase):
    """Entry creation schema."""

    pass


class EntryUpdate(BaseModel):
    """Entry update schema."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    kind: Optional[EntryKind] = None
    link: Optional[str] = None
    status: Optional[EntryStatus] = None
    description: Optional[str] = Field(None, max_length=5000)

    @field_validator("kind")
    @classmethod
    def validate_kind(cls, v: Optional[EntryKind]) -> Optional[str]:
        """Validate entry kind."""
        if v is None:
            return None
        if isinstance(v, EntryKind):
            return v.value
        if v not in [k.value for k in EntryKind]:
            raise ValueError(
                f"Invalid kind. Must be one of: {[k.value for k in EntryKind]}"
            )
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[EntryStatus]) -> Optional[str]:
        """Validate entry status."""
        if v is None:
            return None
        if isinstance(v, EntryStatus):
            return v.value
        if v not in [s.value for s in EntryStatus]:
            raise ValueError(
                f"Invalid status. Must be one of: {[s.value for s in EntryStatus]}"
            )
        return v


class EntryResponse(EntryBase):
    """Entry response schema."""

    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EntryListResponse(BaseModel):
    """Entry list response schema."""

    items: list[EntryResponse]
    total: int
    limit: int
    offset: int
