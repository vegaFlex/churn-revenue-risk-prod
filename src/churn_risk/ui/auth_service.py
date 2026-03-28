from __future__ import annotations

from typing import Any


def build_login_context(
    request,
    error_message: str | None = None,
) -> dict[str, Any]:
    return {
        "page_title": "Sign In",
        "request": request,
        "error_message": error_message,
    }
