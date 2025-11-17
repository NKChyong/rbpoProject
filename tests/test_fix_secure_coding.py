"""Regression tests for P06 security controls."""

import pytest
from pydantic import ValidationError

from app.core.http_client import SecureHTTPClient
from app.domain.schemas import EntryCreate, UserCreate


class TestPasswordPolicy:
    """Ensure strengthened password policy rejects weak secrets."""

    def test_user_create_rejects_weak_password(self):
        """Passwords without sufficient complexity must raise validation error."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="weak@example.com",
                username="weakuser",
                password="password123",
            )


class TestEntryLinkValidation:
    """Verify entry link validation blocks insecure targets."""

    @pytest.mark.parametrize(
        "link",
        [
            "http://example.com/insecure",
            "https://127.0.0.1/admin",
            "https://localhost/dashboard",
            "https://printer.local/resource",
        ],
    )
    def test_entry_create_rejects_insecure_links(self, link):
        """Non-HTTPS or private-network links should not pass validation."""
        with pytest.raises(ValidationError):
            EntryCreate(
                title="Test resource",
                kind="book",
                link=link,
                status="to_read",
            )


class TestSecureHTTPClient:
    """Confirm SecureHTTPClient prevents SSRF to private networks."""

    @pytest.mark.asyncio
    async def test_client_blocks_private_network_requests(self):
        """Fetching from loopback should fail before making the request."""
        client = SecureHTTPClient()
        with pytest.raises(ValueError):
            await client.get("https://127.0.0.1/secret")
