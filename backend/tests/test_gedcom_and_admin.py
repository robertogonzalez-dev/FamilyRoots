from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient

from app.services.gedcom_importer import _parse_gedcom_date
from tests.conftest import Headers

SAMPLE = Path(__file__).parent / "fixtures" / "sample.ged"


def _upload(client: TestClient, headers: Headers, name: str = "family.ged", data: bytes | None = None):
    content = SAMPLE.read_bytes() if data is None else data
    return client.post("/gedcom/import", files={"file": (name, content)}, headers=headers)


def test_parse_gedcom_dates() -> None:
    assert _parse_gedcom_date("12 MAR 1890") == date(1890, 3, 12)
    assert _parse_gedcom_date("ABT 1960") == date(1960, 1, 1)
    assert _parse_gedcom_date("AUG 1985") == date(1985, 8, 1)
    assert _parse_gedcom_date("") is None
    assert _parse_gedcom_date("sometime") is None


def test_import_people_relationships_and_living_status(
    client: TestClient, admin: Headers
) -> None:
    resp = _upload(client, admin)
    assert resp.status_code == 200
    result = resp.json()["result"]
    assert result["persons_created"] == 4
    assert result["relationships_created"] == 5  # 1 spouse + 2 children x 2 parents
    assert result["errors"] == ["Child @I99@ not found"]

    people = {p["full_name"].split()[0]: p for p in client.get("/people", headers=admin).json()}
    assert set(people) == {"Jose", "Rosa", "Miguel", "Ana"}

    def living(name: str) -> bool:
        return client.get(f"/people/{people[name]['id']}", headers=admin).json()["is_living"]

    assert living("Jose") is False  # has a death date
    assert living("Rosa") is False  # "1 DEAT Y": deceased, date unknown
    assert living("Miguel") is False  # born 1880, presumed deceased
    assert living("Ana") is True  # born 1985, no death record

    detail = client.get(f"/people/{people['Jose']['id']}", headers=admin).json()
    assert detail["middle_name"] == "Luis"
    assert detail["birth_place"] == "Guadalajara, Jalisco, Mexico"


def test_reimport_is_idempotent(client: TestClient, admin: Headers) -> None:
    _upload(client, admin)
    result = _upload(client, admin).json()["result"]
    assert result["persons_created"] == 0
    assert result["persons_skipped"] == 4
    assert result["relationships_created"] == 0


def test_import_requires_admin_and_gedcom_file(
    client: TestClient, admin: Headers, editor: Headers
) -> None:
    assert _upload(client, editor).status_code == 403
    assert _upload(client, admin, name="family.txt").status_code == 400


def test_admin_dashboard_and_self_protection(
    client: TestClient, admin: Headers, viewer: Headers
) -> None:
    _upload(client, admin)
    stats = client.get("/admin/dashboard", headers=admin).json()
    assert stats["total_people"] == 4 and stats["living_people"] == 1
    assert client.get("/admin/dashboard", headers=viewer).status_code == 403

    users = {u["email"]: u["id"] for u in client.get("/admin/users", headers=admin).json()}
    me = users["admin@example.com"]
    assert client.patch(f"/admin/users/{me}", json={"role": "viewer"}, headers=admin).status_code == 400
    assert client.patch(f"/admin/users/{me}", json={"is_active": False}, headers=admin).status_code == 400
    assert client.delete(f"/admin/users/{me}", headers=admin).status_code == 400

    other = users["viewer@example.com"]
    promoted = client.patch(f"/admin/users/{other}", json={"role": "editor"}, headers=admin)
    assert promoted.json()["role"] == "editor"
