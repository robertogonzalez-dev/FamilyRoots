from collections.abc import Callable

import bcrypt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.config import DEFAULT_SECRET_KEY, Settings
from app.models.user import User, UserRole
from tests.conftest import PASSWORD, Headers


def _register(client: TestClient, email: str = "Ana@Example.com", password: str = PASSWORD):
    return client.post(
        "/auth/register", json={"email": email, "password": password, "full_name": "Ana"}
    )


def test_health(client: TestClient) -> None:
    assert client.get("/health").json()["status"] == "ok"


def test_register_creates_viewer_and_login_is_case_insensitive(
    client: TestClient, login: Callable[[str], Headers]
) -> None:
    resp = _register(client)
    assert resp.status_code == 201
    assert resp.json()["role"] == "viewer"
    assert resp.json()["email"] == "ana@example.com"
    me = client.get("/auth/me", headers=login("ANA@example.com"))
    assert me.json()["email"] == "ana@example.com"


def test_duplicate_email_and_short_password(client: TestClient) -> None:
    assert _register(client).status_code == 201
    assert _register(client, email="ana@EXAMPLE.com").status_code == 400
    assert _register(client, email="bob@example.com", password="short").status_code == 422


def test_bad_credentials_and_tokens(client: TestClient) -> None:
    _register(client)
    bad = client.post("/auth/login", data={"username": "ana@example.com", "password": "wrong-pass"})
    assert bad.status_code == 401
    assert client.get("/auth/me", headers={"Authorization": "Bearer junk"}).status_code == 401
    assert client.get("/people").status_code == 401


def test_inactive_user_cannot_log_in(
    client: TestClient, db_session: sessionmaker[Session]
) -> None:
    _register(client)
    with db_session() as db:
        db.query(User).one().is_active = False
        db.commit()
    resp = client.post("/auth/login", data={"username": "ana@example.com", "password": PASSWORD})
    assert resp.status_code == 401


def test_legacy_bcrypt_hash_still_works_and_is_upgraded(
    client: TestClient, db_session: sessionmaker[Session], login: Callable[[str], Headers]
) -> None:
    """Accounts created with the old passlib/bcrypt setup must keep working."""
    legacy = bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt()).decode()
    with db_session() as db:
        db.add(User(email="old@example.com", password_hash=legacy, full_name="Old", role=UserRole.viewer))
        db.commit()

    login("old@example.com")

    with db_session() as db:
        assert db.query(User).one().password_hash.startswith("$argon2")


def test_production_rejects_default_secret() -> None:
    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(APP_ENV="production", SECRET_KEY=DEFAULT_SECRET_KEY)
    Settings(APP_ENV="production", SECRET_KEY="x" * 40)  # a real secret is fine
