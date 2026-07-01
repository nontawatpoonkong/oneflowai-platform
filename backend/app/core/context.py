"""Request-scoped context propagated via contextvars.

These carry identifiers across the async call stack (middleware -> service
-> repository) so logging can attach them automatically without threading
them through every function signature.

Sprint 1 - Step 1 populates only `request_id` (via middleware).
`workspace_id` / `user_id` are wired here as foundation and will be set by
the auth layer in a later sprint.
"""

import contextvars

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)
workspace_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "workspace_id", default=None
)
user_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "user_id", default=None
)


def set_request_id(value: str | None) -> contextvars.Token:
    return request_id_var.set(value)


def set_workspace_id(value: str | None) -> contextvars.Token:
    return workspace_id_var.set(value)


def set_user_id(value: str | None) -> contextvars.Token:
    return user_id_var.set(value)


def get_request_id() -> str | None:
    return request_id_var.get()


def get_log_context() -> dict[str, str]:
    """Return only the context values that are currently set (non-None)."""
    context: dict[str, str] = {}
    if (rid := request_id_var.get()) is not None:
        context["request_id"] = rid
    if (wid := workspace_id_var.get()) is not None:
        context["workspace_id"] = wid
    if (uid := user_id_var.get()) is not None:
        context["user_id"] = uid
    return context
