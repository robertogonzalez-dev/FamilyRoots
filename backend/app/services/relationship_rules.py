"""Integrity rules for the family graph.

Direction convention (matches the frontend): for parent-like types, person1 is the parent
and person2 is the child. Spouse and sibling links are symmetric.
"""
from collections import deque

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.person import Person
from app.models.relationship import Relationship, RelationshipType

PARENT_LIKE = (
    RelationshipType.parent_child,
    RelationshipType.adopted_child,
    RelationshipType.step_parent,
)
SYMMETRIC = (RelationshipType.spouse, RelationshipType.sibling)
MAX_BIOLOGICAL_PARENTS = 2


def _parents_of(db: Session, person_id: int) -> list[int]:
    rows = db.query(Relationship.person1_id).filter(
        Relationship.person2_id == person_id,
        Relationship.relationship_type.in_(PARENT_LIKE),
    )
    return [r[0] for r in rows]


def _is_ancestor(db: Session, candidate_id: int, person_id: int) -> bool:
    """True if candidate_id appears anywhere above person_id in the tree."""
    seen = {person_id}
    queue = deque([person_id])
    while queue:
        for parent in _parents_of(db, queue.popleft()):
            if parent == candidate_id:
                return True
            if parent not in seen:
                seen.add(parent)
                queue.append(parent)
    return False


def validate_new_relationship(
    db: Session, person1_id: int, person2_id: int, rel_type: RelationshipType
) -> str | None:
    """Return an error message if the relationship should be rejected, else None."""
    if person1_id == person2_id:
        return "A person cannot be related to themselves."

    found = {p.id for p in db.query(Person.id).filter(Person.id.in_([person1_id, person2_id]))}
    missing = {person1_id, person2_id} - found
    if missing:
        return f"Person {min(missing)} does not exist."

    same_direction = and_(
        Relationship.person1_id == person1_id, Relationship.person2_id == person2_id
    )
    either_direction = or_(
        same_direction,
        and_(Relationship.person1_id == person2_id, Relationship.person2_id == person1_id),
    )
    duplicate = db.query(Relationship).filter(
        either_direction if rel_type in SYMMETRIC else same_direction,
        Relationship.relationship_type == rel_type,
    )
    if db.query(duplicate.exists()).scalar():
        return "This relationship already exists."

    if rel_type in PARENT_LIKE:
        # person1 becomes a parent of person2; reject if person2 is already above person1.
        if _is_ancestor(db, candidate_id=person2_id, person_id=person1_id):
            return "That link would make someone their own ancestor."
        if rel_type == RelationshipType.parent_child:
            biological = db.query(Relationship).filter(
                Relationship.person2_id == person2_id,
                Relationship.relationship_type == RelationshipType.parent_child,
            ).count()
            if biological >= MAX_BIOLOGICAL_PARENTS:
                return (
                    f"Person {person2_id} already has {MAX_BIOLOGICAL_PARENTS} biological parents. "
                    "Use adopted_child or step_parent for additional parents."
                )
    return None
