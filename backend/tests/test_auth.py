from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_register_login_me(client: TestClient, auth: dict[str, str]) -> None:
    me = client.get("/auth/me", headers=auth)
    assert me.status_code == 200
    assert me.json()["email"] == "ana@example.com"


def test_duplicate_email_rejected(client: TestClient, auth: dict[str, str]) -> None:
    body = {"email": "ANA@example.com", "password": "another-pass", "display_name": "A"}
    assert client.post("/auth/register", json=body).status_code == 409


def test_bad_password(client: TestClient, auth: dict[str, str]) -> None:
    resp = client.post("/auth/login", data={"username": "ana@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_invalid_token(client: TestClient) -> None:
    assert client.get("/auth/me", headers={"Authorization": "Bearer junk"}).status_code == 401
    assert client.get("/trees").status_code == 401
