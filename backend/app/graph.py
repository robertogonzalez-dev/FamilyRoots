"""Family-graph rules and traversals over parent relationships."""

from __future__ import annotations

from collections import deque

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import RelationKind, Relationship

MAX_PARENTS = 2


def parents_of(db: Session, person_id: int) -> list[int]:
    stmt = select(Relationship.person_a_id).where(
        Relationship.person_b_id == person_id, Relationship.kind == RelationKind.parent
    )
    return list(db.scalars(stmt))


def ancestors(db: Session, person_id: int, max_generations: int) -> list[tuple[int, int]]:
    """Breadth-first walk up the tree; returns (person_id, generation) pairs."""
    seen: set[int] = {person_id}
    out: list[tuple[int, int]] = []
    queue: deque[tuple[int, int]] = deque([(person_id, 0)])
    while queue:
        current, gen = queue.popleft()
        if gen == max_generations:
            continue
        for parent in parents_of(db, current):
            if parent not in seen:
                seen.add(parent)
                out.append((parent, gen + 1))
                queue.append((parent, gen + 1))
    return out


def validate_parent_link(db: Session, parent_id: int, child_id: int) -> str | None:
    """Return an error message if linking parent -> child would break the family graph."""
    if len(parents_of(db, child_id)) >= MAX_PARENTS:
        return f"Person {child_id} already has {MAX_PARENTS} parents."
    # A cycle appears if the child is already an ancestor of the would-be parent.
    if any(pid == child_id for pid, _ in ancestors(db, parent_id, max_generations=10_000)):
        return "That link would make a person their own ancestor."
    return None
