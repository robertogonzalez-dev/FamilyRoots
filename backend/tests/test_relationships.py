from collections.abc import Callable

from fastapi.testclient import TestClient

from tests.conftest import Headers


def test_rejects_self_missing_and_duplicate_links(
    add_person: Callable[..., int], link: Callable[..., int]
) -> None:
    a, b = add_person("A"), add_person("B")
    assert link(a, a) == 422
    assert link(a, 999) == 422
    assert link(a, b, "spouse") == 201
    assert link(b, a, "spouse") == 422  # symmetric duplicate
    assert link(a, b) == 201  # different type between the same two people is allowed
    assert link(a, b) == 422


def test_rejects_cycles(add_person: Callable[..., int], link: Callable[..., int]) -> None:
    grandma, mom, kid = add_person("G"), add_person("M"), add_person("K")
    assert link(grandma, mom) == 201
    assert link(mom, kid) == 201
    assert link(kid, grandma) == 422  # would make grandma her own descendant
    assert link(kid, grandma, "adopted_child") == 422  # adoption can't create a cycle either


def test_at_most_two_biological_parents(
    add_person: Callable[..., int], link: Callable[..., int]
) -> None:
    kid = add_person("K")
    mom, dad, stepdad, adoptive = (add_person(n) for n in ["M", "D", "S", "A"])
    assert link(mom, kid) == 201
    assert link(dad, kid) == 201
    assert link(stepdad, kid) == 422
    assert link(stepdad, kid, "step_parent") == 201
    assert link(adoptive, kid, "adopted_child") == 201


def test_changing_type_is_validated(
    client: TestClient, editor: Headers, add_person: Callable[..., int], link: Callable[..., int]
) -> None:
    kid, mom, dad, step = (add_person(n) for n in ["K", "M", "D", "S"])
    link(mom, kid)
    link(dad, kid)
    link(step, kid, "step_parent")
    step_rel = next(
        r["id"]
        for r in client.get("/relationships", headers=editor).json()
        if r["relationship_type"] == "step_parent"
    )
    resp = client.patch(
        f"/relationships/{step_rel}", json={"relationship_type": "parent_child"}, headers=editor
    )
    assert resp.status_code == 422
    ok = client.patch(f"/relationships/{step_rel}", json={"notes": "Married 1990"}, headers=editor)
    assert ok.json()["notes"] == "Married 1990"


def test_relatives_endpoint(
    client: TestClient, editor: Headers, add_person: Callable[..., int], link: Callable[..., int]
) -> None:
    mom, kid, sibling, spouse = (add_person(n) for n in ["Maria", "Kid", "Sib", "Spouse"])
    link(mom, kid)
    link(mom, sibling)
    link(kid, spouse, "spouse")
    rel = client.get(f"/people/{kid}/relatives", headers=editor).json()
    assert [p["id"] for p in rel["parents"]] == [mom]
    assert [p["id"] for p in rel["siblings"]] == [sibling]  # derived from the shared parent
    assert [p["id"] for p in rel["spouses"]] == [spouse]
