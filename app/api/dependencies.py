from typing import Any

from fastapi import Request


def get_db(request: Request) -> Any:
    return request.state.db


def is_htmx(request: Request) -> bool:
    """Checks if the request was made by HTMX."""
    htmx_request = request.headers.get("HX-Request", "false")
    return str(htmx_request).lower() == "true"
