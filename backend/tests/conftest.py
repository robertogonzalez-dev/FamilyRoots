from collections.abc import Callable, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override() -> Iterator[Session]:
        with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def signup(client: TestClient) -> Callable[[str], dict[str, str]]:
    """Register + log in a user, returning auth headers."""

    def _signup(email: str = "ana@example.com") -> dict[str, str]:
        client.post(
            "/auth/register",
            json={"email": email, "password": "correct-horse", "display_name": "Ana"},
        )
        token = client.post(
            "/auth/login", data={"username": email, "password": "correct-horse"}
        ).json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _signup


@pytest.fixture
def auth(signup: Callable[[str], dict[str, str]]) -> dict[str, str]:
    return signup("ana@example.com")
