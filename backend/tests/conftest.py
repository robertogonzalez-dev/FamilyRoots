import os
import tempfile
from collections.abc import Callable, Iterator

# Configure the app for tests before anything imports app.config.
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("UPLOAD_DIR", tempfile.mkdtemp(prefix="familyroots-uploads-"))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

import app.models  # noqa: E402,F401  (registers every table)
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import UserRole  # noqa: E402
from app.schemas.user import UserCreate  # noqa: E402
from app.services.user_service import create_user  # noqa: E402

PASSWORD = "correct-horse-battery"

Headers = dict[str, str]


@pytest.fixture
def db_session() -> Iterator[sessionmaker[Session]]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, autoflush=False, autocommit=False)
    engine.dispose()


@pytest.fixture
def client(db_session: sessionmaker[Session]) -> Iterator[TestClient]:
    def override() -> Iterator[Session]:
        with db_session() as session:
            yield session

    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def login(client: TestClient) -> Callable[[str], Headers]:
    def _login(email: str, password: str = PASSWORD) -> Headers:
        resp = client.post("/auth/login", data={"username": email, "password": password})
        assert resp.status_code == 200, resp.text
        return {"Authorization": f"Bearer {resp.json()['access_token']}"}

    return _login


@pytest.fixture
def user_with_role(
    db_session: sessionmaker[Session], login: Callable[[str], Headers]
) -> Callable[[UserRole], Headers]:
    """Create a user with the given role directly in the DB and return auth headers."""

    def _make(role: UserRole) -> Headers:
        email = f"{role.value}@example.com"
        with db_session() as db:
            create_user(db, UserCreate(email=email, password=PASSWORD, full_name=role.value, role=role))
        return login(email)

    return _make


@pytest.fixture
def admin(user_with_role: Callable[[UserRole], Headers]) -> Headers:
    return user_with_role(UserRole.admin)


@pytest.fixture
def editor(user_with_role: Callable[[UserRole], Headers]) -> Headers:
    return user_with_role(UserRole.editor)


@pytest.fixture
def viewer(user_with_role: Callable[[UserRole], Headers]) -> Headers:
    return user_with_role(UserRole.viewer)


@pytest.fixture
def add_person(client: TestClient, editor: Headers) -> Callable[..., int]:
    def _add(first_name: str, is_living: bool = False, **fields: object) -> int:
        body = {"first_name": first_name, "is_living": is_living, **fields}
        resp = client.post("/people", json=body, headers=editor)
        assert resp.status_code == 201, resp.text
        return resp.json()["id"]

    return _add


@pytest.fixture
def link(client: TestClient, editor: Headers) -> Callable[[int, int, str], int]:
    """Create a relationship and return the status code."""

    def _link(person1_id: int, person2_id: int, rel_type: str = "parent_child") -> int:
        body = {"person1_id": person1_id, "person2_id": person2_id, "relationship_type": rel_type}
        return client.post("/relationships", json=body, headers=editor).status_code

    return _link
