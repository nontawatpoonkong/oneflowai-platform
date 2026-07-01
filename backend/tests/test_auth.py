"""Register / login / current-user API tests (against a real Postgres)."""

from fastapi.testclient import TestClient

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/auth/me"


def _register(client: TestClient, **overrides) -> dict:
    payload = {
        "email": "alice@example.com",
        "password": "supersecret123",
        "full_name": "Alice Example",
    }
    payload.update(overrides)
    return client.post(REGISTER_URL, json=payload)


def test_register_creates_user_workspace_and_returns_token(
    client_db: TestClient,
) -> None:
    response = _register(client_db)

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True

    data = body["data"]
    assert data["user"]["email"] == "alice@example.com"
    assert data["user"]["full_name"] == "Alice Example"
    assert "id" in data["user"]

    # Workspace auto-created with the registering user as owner.
    assert data["workspace"]["owner_id"] == data["user"]["id"]
    assert data["workspace"]["slug"]

    # Access token issued (30 min => 1800s).
    assert data["token"]["token_type"] == "bearer"
    assert data["token"]["expires_in"] == 1800
    assert data["token"]["access_token"]


def test_register_rejects_duplicate_email(client_db: TestClient) -> None:
    assert _register(client_db).status_code == 201

    duplicate = _register(client_db)
    assert duplicate.status_code == 409
    body = duplicate.json()
    assert body["success"] is False
    assert body["error"]["code"] == "EMAIL_ALREADY_EXISTS"


def test_register_validates_password_length(client_db: TestClient) -> None:
    response = _register(client_db, password="short")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_login_succeeds_with_valid_credentials(client_db: TestClient) -> None:
    _register(client_db)

    response = client_db.post(
        LOGIN_URL,
        json={"email": "alice@example.com", "password": "supersecret123"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["access_token"]
    assert data["expires_in"] == 1800


def test_login_is_case_insensitive_on_email(client_db: TestClient) -> None:
    _register(client_db)
    response = client_db.post(
        LOGIN_URL,
        json={"email": "ALICE@example.com", "password": "supersecret123"},
    )
    assert response.status_code == 200


def test_login_fails_with_wrong_password(client_db: TestClient) -> None:
    _register(client_db)
    response = client_db.post(
        LOGIN_URL,
        json={"email": "alice@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_me_returns_current_user_with_token(client_db: TestClient) -> None:
    token = _register(client_db).json()["data"]["token"]["access_token"]

    response = client_db.get(ME_URL, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["data"]["email"] == "alice@example.com"


def test_me_requires_authentication(client_db: TestClient) -> None:
    response = client_db.get(ME_URL)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"
