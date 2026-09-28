from collections.abc import Callable

from fastapi.testclient import TestClient


def _tree(client: TestClient, auth: dict[str, str]) -> int:
    return client.post("/trees", json={"name": "Gonzalez"}, headers=auth).json()["id"]


def _person(client: TestClient, auth: dict[str, str], tree: int, name: str) -> int:
    resp = client.post(f"/trees/{tree}/people", json={"given_name": name}, headers=auth)
    assert resp.status_code == 201
    return resp.json()["id"]


def _parent(client: TestClient, auth: dict[str, str], tree: int, parent: int, child: int) -> int:
    body = {"person_a_id": parent, "person_b_id": child, "kind": "parent"}
    return client.post(f"/trees/{tree}/relationships", json=body, headers=auth).status_code


def test_tree_crud(client: TestClient, auth: dict[str, str]) -> None:
    tree = _tree(client, auth)
    assert [t["name"] for t in client.get("/trees", headers=auth).json()] == ["Gonzalez"]
    resp = client.put(f"/trees/{tree}", json={"name": "Gonzalez Family"}, headers=auth)
    assert resp.json()["name"] == "Gonzalez Family"
    assert client.delete(f"/trees/{tree}", headers=auth).status_code == 204
    assert client.get(f"/trees/{tree}", headers=auth).status_code == 404


def test_trees_are_private(client: TestClient, signup: Callable[[str], dict[str, str]]) -> None:
    ana, bob = signup("ana@example.com"), signup("bob@example.com")
    tree = _tree(client, ana)
    assert client.get(f"/trees/{tree}", headers=bob).status_code == 404
    assert client.get("/trees", headers=bob).json() == []


def test_person_crud(client: TestClient, auth: dict[str, str]) -> None:
    tree = _tree(client, auth)
    pid = _person(client, auth, tree, "Rosa")
    body = {"given_name": "Rosa", "family_name": "Gonzalez", "birth_date": "1950-03-01"}
    assert client.put(f"/trees/{tree}/people/{pid}", json=body, headers=auth).status_code == 200
    person = client.get(f"/trees/{tree}/people/{pid}", headers=auth).json()
    assert person["family_name"] == "Gonzalez" and person["birth_date"] == "1950-03-01"
    assert client.delete(f"/trees/{tree}/people/{pid}", headers=auth).status_code == 204
    assert client.get(f"/trees/{tree}/people/{pid}", headers=auth).status_code == 404


def test_relationships_graph_and_ancestors(client: TestClient, auth: dict[str, str]) -> None:
    tree = _tree(client, auth)
    grandma, mom, dad, kid = (_person(client, auth, tree, n) for n in ["G", "M", "D", "K"])
    assert _parent(client, auth, tree, grandma, mom) == 201
    assert _parent(client, auth, tree, mom, kid) == 201
    assert _parent(client, auth, tree, dad, kid) == 201
    spouse = {"person_a_id": dad, "person_b_id": mom, "kind": "spouse"}
    assert client.post(f"/trees/{tree}/relationships", json=spouse, headers=auth).status_code == 201

    graph = client.get(f"/trees/{tree}/graph", headers=auth).json()
    assert len(graph["people"]) == 4 and len(graph["relationships"]) == 4

    ancestors = client.get(f"/trees/{tree}/people/{kid}/ancestors", headers=auth).json()
    assert {(a["person"]["id"], a["generation"]) for a in ancestors} == {
        (mom, 1),
        (dad, 1),
        (grandma, 2),
    }
    one_gen = client.get(f"/trees/{tree}/people/{kid}/ancestors?generations=1", headers=auth)
    assert len(one_gen.json()) == 2


def test_relationship_rules(client: TestClient, auth: dict[str, str]) -> None:
    tree = _tree(client, auth)
    a, b, c, d = (_person(client, auth, tree, n) for n in "ABCD")
    assert _parent(client, auth, tree, a, b) == 201
    assert _parent(client, auth, tree, a, b) == 409  # duplicate
    assert _parent(client, auth, tree, b, a) == 422  # cycle
    assert _parent(client, auth, tree, a, a) == 422  # self
    assert _parent(client, auth, tree, c, b) == 201
    assert _parent(client, auth, tree, d, b) == 422  # third parent


def test_cross_tree_links_rejected(client: TestClient, auth: dict[str, str]) -> None:
    t1, t2 = _tree(client, auth), _tree(client, auth)
    p1, p2 = _person(client, auth, t1, "X"), _person(client, auth, t2, "Y")
    assert _parent(client, auth, t1, p1, p2) == 404


def test_delete_relationship(client: TestClient, auth: dict[str, str]) -> None:
    tree = _tree(client, auth)
    a, b = _person(client, auth, tree, "A"), _person(client, auth, tree, "B")
    body = {"person_a_id": a, "person_b_id": b, "kind": "parent"}
    rel = client.post(f"/trees/{tree}/relationships", json=body, headers=auth).json()["id"]
    assert client.delete(f"/trees/{tree}/relationships/{rel}", headers=auth).status_code == 204
    assert client.delete(f"/trees/{tree}/relationships/{rel}", headers=auth).status_code == 404
