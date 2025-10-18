"""
RFC 7807 Problem Details for HTTP APIs implementation.
Provides standardized error handling with correlation IDs and data masking.
"""

import re
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi.responses import JSONResponse


def mask_sensitive_data(data: str) -> str:
    """
    Mask sensitive data in error messages to prevent information disclosure.

    Args:
        data: String that may contain sensitive information

    Returns:
        String with sensitive data masked
    """
    if not isinstance(data, str):
        return str(data)

    # Email addresses
    data = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "***@***.***", data)

    # Passwords and secrets
    data = re.sub(r"(?i)(password|passwd|pwd)\s*[:=]\s*[^\s]+", r"\1=***", data)
    data = re.sub(r"(?i)(secret|token|key|api_key)\s*[:=]\s*[^\s]+", r"\1=***", data)

    # Credit card numbers
    data = re.sub(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "****-****-****-****", data)

    # Phone numbers
    data = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "***-***-****", data)

    return data


def problem(
    status: int,
    title: str,
    detail: str,
    type_: str = "about:blank",
    extras: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """
    Create RFC 7807 Problem Details response.

    Args:
        status: HTTP status code
        title: Short, human-readable summary
        detail: Human-readable explanation specific to this occurrence
        type_: URI that identifies the problem type
        extras: Additional fields for the problem details

    Returns:
        JSONResponse with RFC 7807 format
    """
    correlation_id = str(uuid4())

    # Mask sensitive data in detail
    masked_detail = mask_sensitive_data(detail)

    # Limit detail length to prevent information disclosure
    if len(masked_detail) > 1000:
        masked_detail = masked_detail[:997] + "..."

    payload = {
        "type": type_,
        "title": title,
        "status": status,
        "detail": masked_detail,
        "correlation_id": correlation_id,
    }

    if extras:
        # Mask sensitive data in extras
        masked_extras = {}
        for key, value in extras.items():
            if isinstance(value, str):
                masked_extras[key] = mask_sensitive_data(value)
            else:
                masked_extras[key] = value
        payload.update(masked_extras)

    return JSONResponse(payload, status_code=status)


def validation_error_problem(field: str, message: str, value: Any = None) -> JSONResponse:
    """
    Create validation error problem details.

    Args:
        field: Field name that failed validation
        message: Validation error message
        value: Invalid value (will be masked)

    Returns:
        JSONResponse with validation error details
    """
    detail = f"Validation failed for field '{field}': {message}"
    if value is not None:
        detail += f" (value: {mask_sensitive_data(str(value))})"

    return problem(
        status=422,
        title="Validation Error",
        detail=detail,
        type_="https://readinglist-api.com/problems/validation-error",
        extras={
            "field": field,
            "invalid_value": mask_sensitive_data(str(value)) if value is not None else None,
        },
    )


def authentication_error_problem(detail: str = "Authentication required") -> JSONResponse:
    """
    Create authentication error problem details.

    Args:
        detail: Authentication error details

    Returns:
        JSONResponse with authentication error details
    """
    return problem(
        status=401,
        title="Authentication Required",
        detail=detail,
        type_="https://readinglist-api.com/problems/authentication-error",
    )


def authorization_error_problem(detail: str = "Insufficient permissions") -> JSONResponse:
    """
    Create authorization error problem details.

    Args:
        detail: Authorization error details

    Returns:
        JSONResponse with authorization error details
    """
    return problem(
        status=403,
        title="Access Denied",
        detail=detail,
        type_="https://readinglist-api.com/problems/authorization-error",
    )


def not_found_problem(resource: str, identifier: str) -> JSONResponse:
    """
    Create not found error problem details.

    Args:
        resource: Type of resource not found
        identifier: Identifier of the resource

    Returns:
        JSONResponse with not found error details
    """
    return problem(
        status=404,
        title="Resource Not Found",
        detail=f"{resource} with identifier '{identifier}' not found",
        type_="https://readinglist-api.com/problems/not-found",
        extras={"resource": resource, "identifier": mask_sensitive_data(identifier)},
    )


def internal_error_problem(detail: str = "An internal error occurred") -> JSONResponse:
    """
    Create internal server error problem details.

    Args:
        detail: Internal error details (will be masked)

    Returns:
        JSONResponse with internal error details
    """
    return problem(
        status=500,
        title="Internal Server Error",
        detail=detail,
        type_="https://readinglist-api.com/problems/internal-error",
    )
