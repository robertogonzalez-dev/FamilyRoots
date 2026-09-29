from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_editor
from app.database import get_db
from app.models.relationship import Relationship
from app.models.user import User
from app.schemas.relationship import RelationshipCreate, RelationshipResponse, RelationshipUpdate
from app.services.privacy_service import can_view_person
from app.services.relationship_rules import validate_new_relationship

router = APIRouter()


def _visible(rel: Relationship, user: User) -> bool:
    """A relationship reveals both people, so it is only visible if both of them are."""
    return can_view_person(rel.person1, user) and can_view_person(rel.person2, user)


@router.get("", response_model=list[RelationshipResponse])
def list_relationships(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return [r for r in db.query(Relationship).all() if _visible(r, current_user)]


@router.post("", response_model=RelationshipResponse, status_code=201)
def create_relationship(
    data: RelationshipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    error = validate_new_relationship(
        db, data.person1_id, data.person2_id, data.relationship_type
    )
    if error:
        raise HTTPException(status_code=422, detail=error)
    rel = Relationship(**data.model_dump())
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel


@router.get("/{rel_id}", response_model=RelationshipResponse)
def get_relationship(rel_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rel = db.query(Relationship).filter(Relationship.id == rel_id).first()
    # 404 (not 403) so hidden relationships aren't discoverable by ID.
    if not rel or not _visible(rel, current_user):
        raise HTTPException(status_code=404, detail="Relationship not found")
    return rel


@router.patch("/{rel_id}", response_model=RelationshipResponse)
def update_relationship(
    rel_id: int,
    data: RelationshipUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    rel = db.query(Relationship).filter(Relationship.id == rel_id).first()
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found")
    if data.relationship_type and data.relationship_type != rel.relationship_type:
        error = validate_new_relationship(db, rel.person1_id, rel.person2_id, data.relationship_type)
        if error:
            raise HTTPException(status_code=422, detail=error)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(rel, field, value)
    db.commit()
    db.refresh(rel)
    return rel


@router.delete("/{rel_id}", status_code=204)
def delete_relationship(
    rel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    rel = db.query(Relationship).filter(Relationship.id == rel_id).first()
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found")
    db.delete(rel)
    db.commit()
