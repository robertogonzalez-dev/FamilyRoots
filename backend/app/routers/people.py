from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_editor
from app.database import get_db
from app.models.person import Person
from app.models.relationship import Relationship, RelationshipType
from app.models.user import User
from app.schemas.person import PersonCreate, PersonResponse, PersonSummary, PersonUpdate
from app.services.privacy_service import can_view_person, filter_people

router = APIRouter()


@router.get("", response_model=list[PersonSummary])
def list_people(
    search: Optional[str] = Query(None, description="Search by name"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Person)
    if search:
        term = f"%{search}%"
        q = q.filter(
            (Person.first_name.ilike(term))
            | (Person.last_name.ilike(term))
            | (Person.maiden_name.ilike(term))
        )
    people = q.offset(skip).limit(limit).all()
    return filter_people(people, current_user)


@router.post("", response_model=PersonResponse, status_code=201)
def create_person(
    data: PersonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    if data.external_id:
        exists = db.query(Person).filter(Person.external_id == data.external_id).first()
        if exists:
            raise HTTPException(status_code=400, detail="Person with this external_id already exists")
    person = Person(**data.model_dump())
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


@router.get("/{person_id}", response_model=PersonResponse)
def get_person(
    person_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    if not can_view_person(person, current_user):
        raise HTTPException(status_code=403, detail="Access denied")
    return person


@router.patch("/{person_id}", response_model=PersonResponse)
def update_person(
    person_id: int,
    data: PersonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(person, field, value)
    db.commit()
    db.refresh(person)
    return person


@router.delete("/{person_id}", status_code=204)
def delete_person(
    person_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    db.delete(person)
    db.commit()


@router.get("/{person_id}/relatives", response_model=dict)
def get_relatives(
    person_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    if not can_view_person(person, current_user):
        raise HTTPException(status_code=403, detail="Access denied")

    rels = db.query(Relationship).filter(
        (Relationship.person1_id == person_id) | (Relationship.person2_id == person_id)
    ).all()

    parents, children, spouses = [], [], []
    parent_ids: list[int] = []
    seen_sibling_ids: set[int] = set()
    siblings: list[dict] = []

    def make_summary(p: Person) -> dict:
        return {
            "id": p.id,
            "full_name": p.full_name,
            "birth_date": p.birth_date.isoformat() if p.birth_date else None,
            "death_date": p.death_date.isoformat() if p.death_date else None,
            "gender": p.gender.value,
            "profile_photo_url": p.profile_photo_url,
        }

    for r in rels:
        other_id = r.person2_id if r.person1_id == person_id else r.person1_id
        other = db.query(Person).filter(Person.id == other_id).first()
        if not other or not can_view_person(other, current_user):
            continue
        if r.relationship_type == RelationshipType.parent_child:
            if r.person1_id == person_id:
                children.append(make_summary(other))
            else:
                parents.append(make_summary(other))
                parent_ids.append(other_id)
        elif r.relationship_type == RelationshipType.spouse:
            spouses.append(make_summary(other))
        elif r.relationship_type == RelationshipType.sibling:
            seen_sibling_ids.add(other_id)
            siblings.append(make_summary(other))

    # Derive siblings from shared parents (covers GEDCOM-imported data)
    if parent_ids:
        sibling_rels = db.query(Relationship).filter(
            Relationship.person1_id.in_(parent_ids),
            Relationship.relationship_type == RelationshipType.parent_child,
            Relationship.person2_id != person_id,
        ).all()
        for sr in sibling_rels:
            if sr.person2_id in seen_sibling_ids:
                continue
            sib = db.query(Person).filter(Person.id == sr.person2_id).first()
            if sib and can_view_person(sib, current_user):
                seen_sibling_ids.add(sr.person2_id)
                siblings.append(make_summary(sib))

    return {"parents": parents, "children": children, "spouses": spouses, "siblings": siblings}
