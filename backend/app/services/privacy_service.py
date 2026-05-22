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
