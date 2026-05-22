"""
GEDCOM 5.5.x importer.
Parses a GEDCOM file (bytes) and inserts People + Relationships into the DB.
Uses a hand-rolled parser so there's no external GEDCOM library dependency.
"""
import logging
import re
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from app.models.person import Person, Gender
from app.models.relationship import Relationship, RelationshipType

logger = logging.getLogger(__name__)

# ── Month abbreviation → number ────────────────────────────────────────────
_MONTH_MAP = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}


def _parse_gedcom_date(value: str) -> Optional[date]:
    """Best-effort parse of a GEDCOM date string → Python date or None."""
    if not value:
        return None
    value = value.strip().upper()
    # Strip qualifiers like ABT, BEF, AFT, EST, CAL
    value = re.sub(r"^(ABT|BEF|AFT|EST|CAL|CIRCA|ABOUT)\s*", "", value)
    parts = value.split()
    try:
        if len(parts) == 3:
            day, month_str, year = parts
            return date(int(year), _MONTH_MAP.get(month_str, 1), int(day))
        if len(parts) == 2:
            month_str, year = parts
            return date(int(year), _MONTH_MAP.get(month_str, 1), 1)
        if len(parts) == 1 and parts[0].isdigit():
            return date(int(parts[0]), 1, 1)
    except (ValueError, KeyError):
        pass
    return None


def _parse_gender(value: str) -> Gender:
    v = (value or "").strip().upper()
    if v == "M":
        return Gender.male
    if v == "F":
        return Gender.female
    return Gender.unknown


# ── Raw record parser ───────────────────────────────────────────────────────

def _tokenize(content: bytes) -> list[tuple[int, str, str]]:
    """Return list of (level, tag, value) tuples."""
    lines = []
    for raw in content.decode("utf-8", errors="replace").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        parts = raw.split(None, 2)
        if len(parts) < 2:
            continue
        level = int(parts[0])
        tag = parts[1]
        value = parts[2] if len(parts) == 3 else ""
        lines.append((level, tag, value))
    return lines


def _build_records(tokens: list) -> dict:
    """Group level-0 records by their XREFs."""
    records: dict[str, dict] = {}
    current_xref = None
    current_record: list = []

    for level, tag, value in tokens:
        if level == 0:
            if current_xref:
                records[current_xref] = current_record
            if tag.startswith("@") and value:
                current_xref = tag          # e.g. @I001@
                current_record = [(level, value, "")]  # value = INDI/FAM
            else:
                current_xref = None
                current_record = []
        else:
            if current_xref is not None:
                current_record.append((level, tag, value))

    if current_xref and current_record:
        records[current_xref] = current_record

    return records


def _get_event_values(record: list, event_tag: str) -> tuple[Optional[date], Optional[str]]:
    """Return (date, place) for a given event tag within a record's sub-lines."""
    in_event = False
    evt_date = None
    evt_place = None
    for level, tag, value in record:
        if level == 1 and tag == event_tag:
            in_event = True
            continue
        if in_event:
            if level <= 1:
                break
            if tag == "DATE":
                evt_date = _parse_gedcom_date(value)
            elif tag == "PLAC":
                evt_place = value
    return evt_date, evt_place


# ── Public import function ──────────────────────────────────────────────────

def import_gedcom(db: Session, content: bytes) -> dict:
    tokens = _tokenize(content)
    records = _build_records(tokens)

    persons_created = 0
    persons_skipped = 0
    relationships_created = 0
    errors: list[str] = []

    xref_to_db_id: dict[str, int] = {}

    # ── Pass 1: individuals ──────────────────────────────────────────────
    for xref, record in records.items():
        if not record or record[0][1] != "INDI":
            continue

        external_id = xref.strip("@")

        # Skip if already imported
        existing = db.query(Person).filter(Person.external_id == external_id).first()
        if existing:
            xref_to_db_id[xref] = existing.id
            persons_skipped += 1
            continue

        # Gather fields
        given = sur = ""
        maiden = middle = None
        gender = Gender.unknown

        birth_date, birth_place = _get_event_values(record, "BIRT")
        death_date, death_place = _get_event_values(record, "DEAT")

        for level, tag, value in record[1:]:
            if level == 1:
                if tag == "NAME":
                    # format: "Given /Surname/"
                    name_val = value
                    match = re.match(r"^(.*?)\s*/([^/]*)/\s*(.*)$", name_val)
                    if match:
                        given = match.group(1).strip()
                        sur = match.group(2).strip()
                        # extra text after surname sometimes has maiden
                    else:
                        parts = name_val.split()
                        given = " ".join(parts[:-1]) if len(parts) > 1 else name_val
                        sur = parts[-1] if len(parts) > 1 else ""
                elif tag == "SEX":
                    gender = _parse_gender(value)

        # Split given into first + middle
        given_parts = given.split()
        first_name = given_parts[0] if given_parts else None
        middle_name = " ".join(given_parts[1:]) if len(given_parts) > 1 else None

        is_living = death_date is None

        person = Person(
            external_id=external_id,
            first_name=first_name,
            middle_name=middle_name,
            last_name=sur or None,
            maiden_name=maiden,
            gender=gender,
            birth_date=birth_date,
            birth_place=birth_place,
            death_date=death_date,
            death_place=death_place,
            is_living=is_living,
        )
        db.add(person)
        db.flush()
        xref_to_db_id[xref] = person.id
        persons_created += 1

    db.commit()

    # ── Pass 2: families ─────────────────────────────────────────────────
    for xref, record in records.items():
        if not record or record[0][1] != "FAM":
            continue

        husb_xref = wife_xref = None
        child_xrefs: list[str] = []

        for level, tag, value in record[1:]:
            if level != 1:
                continue
            if tag == "HUSB":
                husb_xref = value.strip()
            elif tag == "WIFE":
                wife_xref = value.strip()
            elif tag == "CHIL":
                child_xrefs.append(value.strip())

        husb_id = xref_to_db_id.get(husb_xref)
        wife_id = xref_to_db_id.get(wife_xref)

        # Spouse relationship
        if husb_id and wife_id:
            exists = db.query(Relationship).filter(
                Relationship.person1_id == husb_id,
                Relationship.person2_id == wife_id,
                Relationship.relationship_type == RelationshipType.spouse,
            ).first()
            if not exists:
                db.add(Relationship(
                    person1_id=husb_id,
                    person2_id=wife_id,
                    relationship_type=RelationshipType.spouse,
                ))
                relationships_created += 1

        # Parent-child relationships
        for child_xref in child_xrefs:
            child_id = xref_to_db_id.get(child_xref)
            if not child_id:
                errors.append(f"Child {child_xref} not found")
                continue
            for parent_id in filter(None, [husb_id, wife_id]):
                exists = db.query(Relationship).filter(
                    Relationship.person1_id == parent_id,
                    Relationship.person2_id == child_id,
                    Relationship.relationship_type == RelationshipType.parent_child,
                ).first()
                if not exists:
                    db.add(Relationship(
                        person1_id=parent_id,
                        person2_id=child_id,
                        relationship_type=RelationshipType.parent_child,
                    ))
                    relationships_created += 1

    db.commit()
    logger.info(
        "GEDCOM import complete: %d created, %d skipped, %d relationships, %d errors",
        persons_created, persons_skipped, relationships_created, len(errors),
    )
    return {
        "persons_created": persons_created,
        "persons_skipped": persons_skipped,
        "relationships_created": relationships_created,
        "errors": errors[:20],  # cap reported errors
    }
