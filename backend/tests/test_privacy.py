"""Viewers must never learn anything about living people, directly or through linked records."""
from collections.abc import Callable

from fastapi.testclient import TestClient

from tests.conftest import Headers


def test_viewer_cannot_see_living_people(
    client: TestClient, viewer: Headers, editor: Headers, add_person: Callable[..., int]
) -> None:
    grandma = add_person("Rosa", is_living=False)
    cousin = add_person("Luis", is_living=True)

    names = {p["full_name"] for p in client.get("/people", headers=viewer).json()}
    assert names == {"Rosa"}
    assert client.get(f"/people/{cousin}", headers=viewer).status_code == 403
    assert client.get(f"/people/{grandma}", headers=viewer).status_code == 200
    assert len(client.get("/people", headers=editor).json()) == 2


def test_relationships_to_living_people_are_hidden(
    client: TestClient,
    viewer: Headers,
    editor: Headers,
    add_person: Callable[..., int],
    link: Callable[..., int],
) -> None:
    grandma = add_person("Rosa")
    grandpa = add_person("Jose")
    mom = add_person("Maria", is_living=True)
    assert link(grandma, grandpa, "spouse") == 201
    assert link(grandma, mom) == 201

    visible = client.get("/relationships", headers=viewer).json()
    assert [(r["person1_id"], r["person2_id"]) for r in visible] == [(grandma, grandpa)]

    hidden_id = next(
        r["id"] for r in client.get("/relationships", headers=editor).json() if r["person2_id"] == mom
    )
    assert client.get(f"/relationships/{hidden_id}", headers=viewer).status_code == 404
    assert client.get(f"/relationships/{hidden_id}", headers=editor).status_code == 200


def test_media_and_sources_of_living_people_are_hidden(
    client: TestClient, viewer: Headers, editor: Headers, add_person: Callable[..., int]
) -> None:
    living = add_person("Luis", is_living=True)
    source = {"person_id": living, "title": "Birth certificate"}
    assert client.post("/sources", json=source, headers=editor).status_code == 201

    assert client.get(f"/sources/person/{living}", headers=viewer).status_code == 404
    assert client.get(f"/media/person/{living}", headers=viewer).status_code == 404
    assert len(client.get(f"/sources/person/{living}", headers=editor).json()) == 1


def test_media_upload_requires_existing_person(
    client: TestClient, editor: Headers, add_person: Callable[..., int]
) -> None:
    png = ("photo.png", b"\x89PNG\r\n\x1a\n", "image/png")
    assert client.post("/media/person/999", files={"file": png}, headers=editor).status_code == 404
    pid = add_person("Rosa")
    resp = client.post(f"/media/person/{pid}", files={"file": png}, headers=editor)
    assert resp.status_code == 201
    assert resp.json()["file_url"].startswith(f"/uploads/{pid}/")


def test_tree_excludes_living_people_for_viewers(
    client: TestClient,
    viewer: Headers,
    editor: Headers,
    add_person: Callable[..., int],
    link: Callable[..., int],
) -> None:
    grandma = add_person("Rosa")
    mom = add_person("Maria", is_living=True)
    link(grandma, mom)

    viewer_tree = client.get("/tree", headers=viewer).json()
    assert [n["id"] for n in viewer_tree["nodes"]] == [str(grandma)]
    assert viewer_tree["edges"] == []
    assert len(client.get("/tree", headers=editor).json()["edges"]) == 1


def test_viewers_cannot_edit(
    client: TestClient, viewer: Headers, add_person: Callable[..., int]
) -> None:
    pid = add_person("Rosa")
    assert client.post("/people", json={"first_name": "X"}, headers=viewer).status_code == 403
    assert client.delete(f"/people/{pid}", headers=viewer).status_code == 403
