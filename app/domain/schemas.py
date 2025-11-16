"""Pydantic schemas for API request/response models."""

import re
from datetime import datetime
from ipaddress import ip_address, ip_network
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator

from app.domain.models import EntryKind, EntryStatus, UserRole

_DISALLOWED_HOSTS = {"localhost"}
_PRIVATE_NETWORKS = (
    ip_network("0.0.0.0/8"),
    ip_network("10.0.0.0/8"),
    ip_network("127.0.0.0/8"),
    ip_network("169.254.0.0/16"),
    ip_network("172.16.0.0/12"),
    ip_network("192.168.0.0/16"),
    ip_network("::1/128"),
    ip_network("fc00::/7"),
    ip_network("fe80::/10"),
)


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

    password: str = Field(min_length=12, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """Validate password complexity requirements."""
        if len(value) < 12:
            raise ValueError("Password must be at least 12 characters long.")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must include an uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must include a lowercase letter.")
        if not re.search(r"\d", value):
            raise ValueError("Password must include a digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=;'\[\]\\/]", value):
            raise ValueError("Password must include a special character.")
        return value


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
    link: Optional[HttpUrl] = Field(default=None, max_length=2048)
    status: EntryStatus = EntryStatus.TO_READ
    description: Optional[str] = Field(None, max_length=5000)

    @field_validator("kind")
    @classmethod
    def validate_kind(cls, v: EntryKind) -> str:
        """Validate entry kind."""
        if isinstance(v, EntryKind):
            return v.value
        if v not in [k.value for k in EntryKind]:
            raise ValueError(f"Invalid kind. Must be one of: {[k.value for k in EntryKind]}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: EntryStatus) -> str:
        """Validate entry status."""
        if isinstance(v, EntryStatus):
            return v.value
        if v not in [s.value for s in EntryStatus]:
            raise ValueError(f"Invalid status. Must be one of: {[s.value for s in EntryStatus]}")
        return v

    @field_validator("link")
    @classmethod
    def validate_link(cls, value: Optional[HttpUrl]) -> Optional[HttpUrl]:
        """Validate that links use HTTPS and do not target private networks."""
        if value is None:
            return None

        if value.scheme != "https":
            raise ValueError("Link must use HTTPS protocol.")

        host = (value.host or "").lower()
        if host in _DISALLOWED_HOSTS:
            raise ValueError("Link host is not allowed.")

        try:
            ip = ip_address(host)
        except ValueError:
            # Host is not an IP address; block obvious local development domains
            if host.endswith(".local") or host.endswith(".localhost"):
                raise ValueError("Link host is not allowed.")
            return value

        for network in _PRIVATE_NETWORKS:
            if ip in network:
                raise ValueError("Link host is not allowed.")

        return value


class EntryCreate(EntryBase):
    """Entry creation schema."""

    pass


class EntryUpdate(BaseModel):
    """Entry update schema."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    kind: Optional[EntryKind] = None
    link: Optional[HttpUrl] = Field(default=None, max_length=2048)
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
            raise ValueError(f"Invalid kind. Must be one of: {[k.value for k in EntryKind]}")
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
            raise ValueError(f"Invalid status. Must be one of: {[s.value for s in EntryStatus]}")
        return v

    @field_validator("link")
    @classmethod
    def validate_link(cls, value: Optional[HttpUrl]) -> Optional[HttpUrl]:
        """Validate updated links with the same policy as creation."""
        return EntryBase.validate_link(value)


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
