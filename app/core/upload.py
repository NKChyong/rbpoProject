"""
Secure file upload with magic bytes validation and path traversal protection.
Implements security measures for file uploads including magic bytes validation,
path canonicalization, and symlink protection.
"""

import uuid
from pathlib import Path
from typing import Optional, Tuple

# Security constants
MAX_FILE_SIZE = 5_000_000  # 5MB
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg"}
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

# Magic bytes for file type detection
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_SOI = b"\xff\xd8"  # Start of Image
JPEG_EOI = b"\xff\xd9"  # End of Image


def sniff_image_type(data: bytes) -> Optional[str]:
    """
    Detect image type by magic bytes (not just file extension).

    Args:
        data: File content as bytes

    Returns:
        MIME type if detected, None otherwise
    """
    if not data:
        return None

    # PNG detection
    if data.startswith(PNG_MAGIC):
        return "image/png"

    # JPEG detection (must start with SOI and end with EOI)
    if data.startswith(JPEG_SOI) and data.endswith(JPEG_EOI):
        return "image/jpeg"

    return None


def validate_file_size(data: bytes) -> bool:
    """
    Validate file size against security limits.

    Args:
        data: File content as bytes

    Returns:
        True if file size is acceptable
    """
    return len(data) <= MAX_FILE_SIZE


def validate_file_type(data: bytes) -> bool:
    """
    Validate file type by magic bytes.

    Args:
        data: File content as bytes

    Returns:
        True if file type is allowed
    """
    detected_type = sniff_image_type(data)
    return detected_type in ALLOWED_MIME_TYPES


def is_safe_path(base_path: Path, target_path: Path) -> bool:
    """
    Check if target path is within base path (prevent path traversal).

    Args:
        base_path: Base directory path
        target_path: Target file path

    Returns:
        True if path is safe
    """
    try:
        # Resolve both paths to absolute paths
        base_resolved = base_path.resolve()
        target_resolved = target_path.resolve()

        # Check if target is within base
        return str(target_resolved).startswith(str(base_resolved))
    except (OSError, ValueError):
        return False


def check_symlinks(path: Path, base_path: Optional[Path] = None) -> bool:
    """
    Check if any parent directory contains symlinks within the base path.

    Args:
        path: File path to check
        base_path: Base directory to limit symlink checking (optional)

    Returns:
        True if no symlinks found in parent directories (within base_path if provided)
    """
    try:
        # If base_path is provided, only check parents within base_path
        if base_path:
            base_resolved = base_path.resolve()
            path_resolved = path.resolve()
            
            # Only check parents between path and base_path
            current = path_resolved
            while current != base_resolved and current != current.parent:
                if current.is_symlink():
                    return False
                current = current.parent
            return True
        else:
            # Check all parent directories for symlinks
            for parent in path.parents:
                if parent.is_symlink():
                    return False
            return True
    except (OSError, ValueError):
        return False


def secure_save(base_dir: str, filename_hint: str, data: bytes) -> Tuple[bool, str]:
    """
    Securely save uploaded file with comprehensive security checks.

    Args:
        base_dir: Base directory for uploads
        filename_hint: Original filename (for logging only)
        data: File content as bytes

    Returns:
        Tuple of (success, path_or_reason)
    """
    try:
        # Validate file size
        if not validate_file_size(data):
            return False, "file_too_large"

        # Validate file type by magic bytes
        if not validate_file_type(data):
            return False, "invalid_file_type"

        # Get detected MIME type
        detected_type = sniff_image_type(data)
        if not detected_type:
            return False, "unable_to_detect_type"

        # Create base directory if it doesn't exist
        base_path = Path(base_dir)
        base_path.mkdir(parents=True, exist_ok=True)

        # Generate secure filename with UUID
        file_extension = ".png" if detected_type == "image/png" else ".jpg"
        secure_filename = f"{uuid.uuid4()}{file_extension}"

        # Create target path
        target_path = base_path / secure_filename

        # Validate path safety
        if not is_safe_path(base_path, target_path):
            return False, "path_traversal_detected"

        # Check for symlinks in parent directories (only within base_path)
        if not check_symlinks(target_path, base_path):
            return False, "symlink_in_path"

        # Ensure target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file atomically
        temp_path = target_path.with_suffix(target_path.suffix + ".tmp")
        with open(temp_path, "wb") as f:
            f.write(data)

        # Atomic move to final location
        temp_path.replace(target_path)

        return True, str(target_path)

    except OSError as e:
        return False, f"filesystem_error: {str(e)}"
    except Exception as e:
        return False, f"unexpected_error: {str(e)}"


def get_file_info(file_path: str) -> Optional[dict]:
    """
    Get file information for uploaded file.

    Args:
        file_path: Path to uploaded file

    Returns:
        Dictionary with file info or None if file doesn't exist
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return None

        stat = path.stat()
        return {
            "filename": path.name,
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "extension": path.suffix.lower(),
        }
    except (OSError, ValueError):
        return None


def cleanup_upload(file_path: str) -> bool:
    """
    Securely delete uploaded file.

    Args:
        file_path: Path to file to delete

    Returns:
        True if file was deleted successfully
    """
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            return True
        return False
    except (OSError, ValueError):
        return False
