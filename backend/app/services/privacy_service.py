from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.person import Person
from app.models.user import User, UserRole


def can_view_person(person: Person, user: User | None) -> bool:
    """Central privacy gate: admins and editors see everyone; viewers/guests only see non-living."""
    if user is None:
        return not person.is_living
    if user.role == UserRole.admin:
        return True
    if user.role == UserRole.editor:
        return True
    # viewer
    return not person.is_living


def filter_people(people: list[Person], user: User | None) -> list[Person]:
    return [p for p in people if can_view_person(p, user)]


def sanitize_person(person: Person, user: User | None) -> Person | None:
    """Returns None if person should be hidden, or a (possibly redacted) copy."""
    if not can_view_person(person, user):
        return None
    return person


def get_visible_person_or_404(db: Session, person_id: int, user: User | None) -> Person:
    """Load a person the user may see; hidden and missing people are both a 404."""
    person = db.get(Person, person_id)
    if person is None or not can_view_person(person, user):
        raise HTTPException(status_code=404, detail="Person not found")
    return person
