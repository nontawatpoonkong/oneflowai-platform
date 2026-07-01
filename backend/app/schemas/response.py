"""Standard API response envelope.

NOTE: This is the *proposed* platform-wide response format (pending your
confirmation from the Step 1 questions). Every endpoint returns this shape:

    success: { "success": true,  "message": "...", "data": {...}, "error": null }
    failure: { "success": false, "message": "...", "data": null, "error": {...} }
"""

from typing import Any

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    details: Any | None = None


class StandardResponse[T](BaseModel):
    success: bool
    message: str
    data: T | None = None
    error: ErrorDetail | None = None


def success_response(data: Any = None, message: str = "OK") -> dict[str, Any]:
    """Build a success envelope as a plain dict."""
    return {"success": True, "message": message, "data": data, "error": None}


def error_response(message: str, code: str, details: Any = None) -> dict[str, Any]:
    """Build an error envelope as a plain dict."""
    return {
        "success": False,
        "message": message,
        "data": None,
        "error": {"code": code, "details": details},
    }
