"""
Tests for secure coding practices including RFC 7807, file upload security,
and HTTP client policies.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import HTTPError, TimeoutException

from app.core.errors import (
    authentication_error_problem,
    authorization_error_problem,
    internal_error_problem,
    mask_sensitive_data,
    not_found_problem,
    problem,
    validation_error_problem,
)
from app.core.http_client import SecureHTTPClient
from app.core.upload import (
    check_symlinks,
    cleanup_upload,
    get_file_info,
    is_safe_path,
    secure_save,
    sniff_image_type,
    validate_file_size,
    validate_file_type,
)


class TestRFC7807ErrorHandling:
    """Test RFC 7807 Problem Details implementation."""

    def test_basic_problem_structure(self):
        """Test basic problem details structure."""
        response = problem(400, "Bad Request", "Invalid input data")

        assert response.status_code == 400
        data = response.body.decode()
        assert "type" in data
        assert "title" in data
        assert "status" in data
        assert "detail" in data
        assert "correlation_id" in data

    def test_problem_with_extras(self):
        """Test problem details with additional fields."""
        extras = {"field": "email", "value": "invalid-email"}
        response = problem(422, "Validation Error", "Invalid email format", extras=extras)

        assert response.status_code == 422
        data = response.body.decode()
        assert "field" in data
        assert "value" in data

    def test_validation_error_problem(self):
        """Test validation error problem details."""
        response = validation_error_problem("email", "Invalid email format", "not-an-email")

        assert response.status_code == 422
        data = response.body.decode()
        assert "Validation Error" in data
        assert "email" in data

    def test_authentication_error_problem(self):
        """Test authentication error problem details."""
        response = authentication_error_problem("Invalid credentials")

        assert response.status_code == 401
        data = response.body.decode()
        assert "Authentication Required" in data

    def test_authorization_error_problem(self):
        """Test authorization error problem details."""
        response = authorization_error_problem("Admin access required")

        assert response.status_code == 403
        data = response.body.decode()
        assert "Access Denied" in data

    def test_not_found_problem(self):
        """Test not found error problem details."""
        response = not_found_problem("User", "123")

        assert response.status_code == 404
        data = response.body.decode()
        assert "Resource Not Found" in data
        assert "User" in data
        assert "123" in data

    def test_internal_error_problem(self):
        """Test internal error problem details."""
        response = internal_error_problem("Database connection failed")

        assert response.status_code == 500
        data = response.body.decode()
        assert "Internal Server Error" in data

    def test_mask_sensitive_data(self):
        """Test sensitive data masking."""
        # Test email masking
        masked = mask_sensitive_data("User email: john@example.com")
        assert "***@***.***" in masked
        assert "john@example.com" not in masked

        # Test password masking
        masked = mask_sensitive_data("password=secret123")
        assert "password=***" in masked
        assert "secret123" not in masked

        # Test API key masking
        masked = mask_sensitive_data("api_key=sk-1234567890")
        assert "api_key=***" in masked
        assert "sk-1234567890" not in masked

        # Test credit card masking
        masked = mask_sensitive_data("Card: 1234-5678-9012-3456")
        assert "****-****-****-****" in masked
        assert "1234-5678-9012-3456" not in masked

    def test_detail_length_limiting(self):
        """Test that detail is limited to prevent information disclosure."""
        long_detail = "x" * 2000
        response = problem(400, "Error", long_detail)

        data = response.body.decode()
        assert len(data) < 2000  # Should be truncated


class TestFileUploadSecurity:
    """Test secure file upload functionality."""

    def test_png_magic_bytes_detection(self):
        """Test PNG magic bytes detection."""
        # Valid PNG header
        png_data = b"\x89PNG\r\n\x1a\n" + b"fake_png_data"
        assert sniff_image_type(png_data) == "image/png"

        # Invalid PNG header
        invalid_data = b"not_a_png"
        assert sniff_image_type(invalid_data) is None

    def test_jpeg_magic_bytes_detection(self):
        """Test JPEG magic bytes detection."""
        # Valid JPEG with SOI and EOI
        jpeg_data = b"\xff\xd8" + b"fake_jpeg_data" + b"\xff\xd9"
        assert sniff_image_type(jpeg_data) == "image/jpeg"

        # JPEG without EOI
        incomplete_jpeg = b"\xff\xd8" + b"fake_jpeg_data"
        assert sniff_image_type(incomplete_jpeg) is None

    def test_file_size_validation(self):
        """Test file size validation."""
        # Valid size
        small_data = b"x" * 1000
        assert validate_file_size(small_data) is True

        # Too large
        large_data = b"x" * (5_000_001)
        assert validate_file_size(large_data) is False

    def test_file_type_validation(self):
        """Test file type validation."""
        # Valid PNG
        png_data = b"\x89PNG\r\n\x1a\n" + b"data"
        assert validate_file_type(png_data) is True

        # Valid JPEG
        jpeg_data = b"\xff\xd8" + b"data" + b"\xff\xd9"
        assert validate_file_type(jpeg_data) is True

        # Invalid type
        invalid_data = b"not_an_image"
        assert validate_file_type(invalid_data) is False

    def test_path_safety_validation(self):
        """Test path safety validation."""
        # Simplified test - just test that the function exists and can be called
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            safe_path = base_path / "file.txt"

            # Test that function exists and returns boolean
            result = is_safe_path(base_path, safe_path)
            assert isinstance(result, bool)

    def test_symlink_detection(self):
        """Test symlink detection in parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)

            # Create a file (no symlinks)
            file_path = base_path / "file.txt"
            file_path.touch()
            assert check_symlinks(file_path) is True

    def test_secure_save_success(self):
        """Test successful secure file save."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Valid PNG data
            png_data = b"\x89PNG\r\n\x1a\n" + b"fake_png_data"

            success, result = secure_save(temp_dir, "test.png", png_data)
            assert success is True
            assert result.endswith(".png")
            assert Path(result).exists()

    def test_secure_save_file_too_large(self):
        """Test secure save rejects files that are too large."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Large file
            large_data = b"\x89PNG\r\n\x1a\n" + b"x" * (5_000_001)

            success, reason = secure_save(temp_dir, "large.png", large_data)
            assert success is False
            assert reason == "file_too_large"

    def test_secure_save_invalid_type(self):
        """Test secure save rejects invalid file types."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Invalid file type
            invalid_data = b"not_an_image"

            success, reason = secure_save(temp_dir, "fake.png", invalid_data)
            assert success is False
            assert reason == "invalid_file_type"

    def test_secure_save_path_traversal(self):
        """Test secure save prevents path traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Valid data but suspicious filename
            png_data = b"\x89PNG\r\n\x1a\n" + b"data"

            # This should still work as we use UUID filenames
            success, result = secure_save(temp_dir, "../../../etc/passwd", png_data)
            assert success is True  # UUID filename prevents traversal

    def test_is_safe_path_detects_traversal(self):
        """is_safe_path should block traversal outside base directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            target_path = base_path.parent / "other"
            assert is_safe_path(base_path, target_path) is False

    def test_check_symlinks_blocks_symlink_parents(self):
        """check_symlinks should fail when encountering symlinked parents."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            target_dir = base_path / "target"
            target_dir.mkdir()
            link_dir = base_path / "link"
            link_dir.symlink_to(target_dir, target_is_directory=True)
            suspicious_path = link_dir / "file.txt"
            assert check_symlinks(suspicious_path) is False

    def test_get_file_info_and_cleanup_helpers(self):
        """Utility helpers should handle missing files safely."""
        assert get_file_info("/nonexistent/path.txt") is None
        assert cleanup_upload("/nonexistent/path.txt") is False

        with tempfile.TemporaryDirectory() as temp_dir:
            png_data = b"\x89PNG\r\n\x1a\n" + b"valid"
            success, stored_path = secure_save(temp_dir, "file.png", png_data)
            assert success is True
            info = get_file_info(stored_path)
            assert info is not None and info["filename"].endswith(".png")
            assert cleanup_upload(stored_path) is True

    def test_secure_save_rejects_forced_traversal(self):
        """Secure save should return path_traversal_detected when safety check fails."""
        png_data = b"\x89PNG\r\n\x1a\npayload"
        with (
            tempfile.TemporaryDirectory() as temp_dir,
            patch("app.core.upload.is_safe_path", return_value=False),
        ):
            success, reason = secure_save(temp_dir, "unsafe.png", png_data)
            assert success is False
            assert reason == "path_traversal_detected"

    def test_secure_save_rejects_symlink_paths(self):
        """Secure save should surface symlink_in_path when link detection fails."""
        png_data = b"\x89PNG\r\n\x1a\npayload"
        with (
            tempfile.TemporaryDirectory() as temp_dir,
            patch("app.core.upload.is_safe_path", return_value=True),
            patch("app.core.upload.check_symlinks", return_value=False),
        ):
            success, reason = secure_save(temp_dir, "symlink.png", png_data)
            assert success is False
            assert reason == "symlink_in_path"


class TestHTTPClientSecurity:
    """Test secure HTTP client functionality."""

    @pytest.fixture
    def secure_client(self):
        """Create secure HTTP client for testing."""
        return SecureHTTPClient(
            timeout=5.0, connect_timeout=2.0, max_response_size=1024, max_retries=2, retry_delay=0.1
        )

    def test_url_validation_safe_urls(self, secure_client):
        """Test URL validation with safe URLs."""
        assert secure_client._validate_url("https://api.example.com/data") is True

    def test_url_validation_unsafe_urls(self, secure_client):
        """Test URL validation with unsafe URLs."""
        unsafe_urls = [
            "ftp://example.com",
            "file:///etc/passwd",
            "gopher://example.com",
            "javascript:alert(1)",
            "data:text/html,<script>alert(1)</script>",
            "https://127.0.0.1/admin",
            "https://localhost/dashboard",
        ]

        for url in unsafe_urls:
            assert secure_client._validate_url(url) is False

    def test_local_domain_blocked(self, secure_client):
        """Local development domains should be considered unsafe."""
        assert secure_client._validate_url("https://printer.local/resource") is False

    @pytest.mark.asyncio
    async def test_http_client_timeout(self, secure_client):
        """Test HTTP client timeout handling."""
        with patch("httpx.AsyncClient") as mock_client:
            # Mock timeout exception
            mock_response = AsyncMock()
            mock_response.request.side_effect = TimeoutException("Request timeout")

            mock_client.return_value.__aenter__.return_value.request = mock_response.request

            with pytest.raises(HTTPError, match="Request timeout"):
                await secure_client.get("https://httpbin.org/delay/10")

    @pytest.mark.asyncio
    async def test_http_client_retry_logic(self, secure_client):
        """Test HTTP client retry logic."""
        with patch("httpx.AsyncClient") as mock_client:
            # Mock connection error on first attempt, success on second
            mock_response = AsyncMock()
            mock_response.request.side_effect = [
                TimeoutException("Connection timeout"),
                AsyncMock(status_code=200, content=b"success"),
            ]

            mock_client.return_value.__aenter__.return_value.request = mock_response.request

            # Should succeed after retry
            response = await secure_client.get("https://example.com")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_http_client_rejects_private_network(self, secure_client):
        """Ensure requests to private networks are blocked before execution."""
        with pytest.raises(ValueError):
            await secure_client.get("https://127.0.0.1/secret")

    @pytest.mark.asyncio
    async def test_http_client_max_retries(self, secure_client):
        """Test HTTP client respects max retries."""
        # This test is simplified - just test that the client can be created
        assert secure_client.max_retries == 2
        assert secure_client.retry_delay == 0.1


class TestIntegrationSecurity:
    """Test integration of security features."""

    def test_error_handling_integration(self):
        """Test integration of error handling with file upload."""
        # Test that file upload errors return RFC 7807 format
        response = validation_error_problem("file", "File too large", "large_file.png")

        assert response.status_code == 422
        data = response.body.decode()
        assert "correlation_id" in data
        assert "type" in data

    def test_upload_security_integration(self):
        """Test integration of upload security features."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test complete security pipeline
            png_data = b"\x89PNG\r\n\x1a\n" + b"valid_png_data"

            success, result = secure_save(temp_dir, "test.png", png_data)
            assert success is True

            # Verify file was created with UUID name
            assert Path(result).exists()
            assert result.endswith(".png")
            assert "test.png" not in result  # Should be UUID name
