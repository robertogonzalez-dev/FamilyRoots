from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.relationship import Relationship
from app.schemas.relationship import RelationshipCreate, RelationshipUpdate, RelationshipResponse
from app.auth.dependencies import get_current_user, require_editor
from app.models.user import User

router = APIRouter()


@router.get("", response_model=list[RelationshipResponse])
def list_relationships(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Relationship).all()


@router.post("", response_model=RelationshipResponse, status_code=201)
def create_relationship(
    data: RelationshipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    rel = Relationship(**data.model_dump())
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel


@router.get("/{rel_id}", response_model=RelationshipResponse)
def get_relationship(rel_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rel = db.query(Relationship).filter(Relationship.id == rel_id).first()
    if not rel:
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
