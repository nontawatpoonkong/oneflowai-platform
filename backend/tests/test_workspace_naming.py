"""Workspace naming strategy unit tests."""

import pytest

from app.services.workspace_naming import derive_workspace_name


@pytest.mark.parametrize(
    ("email", "full_name", "expected"),
    [
        ("alice@acme.com", "Alice", "Acme Workspace"),
        ("bob@acme.co.uk", None, "Acme Workspace"),
        ("dev@nimble-labs.io", "Dev", "Nimble Labs Workspace"),
    ],
)
def test_company_name_derived_from_domain(email, full_name, expected) -> None:
    assert derive_workspace_name(email=email, full_name=full_name) == expected


@pytest.mark.parametrize(
    ("email", "full_name", "expected"),
    [
        ("alice@gmail.com", "Alice Example", "Alice Example's Workspace"),
        ("bob@yahoo.com", None, "bob's Workspace"),
    ],
)
def test_personal_email_falls_back_to_user_naming(email, full_name, expected) -> None:
    # Backward-compatible behaviour for personal/free email providers.
    assert derive_workspace_name(email=email, full_name=full_name) == expected
