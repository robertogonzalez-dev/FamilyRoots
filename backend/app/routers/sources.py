from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_editor
from app.database import get_db
from app.models.source import Source
from app.models.user import User
from app.schemas.source import SourceCreate, SourceResponse, SourceUpdate
from app.services.privacy_service import get_visible_person_or_404

router = APIRouter()


@router.get("/person/{person_id}", response_model=list[SourceResponse])
def list_person_sources(
    person_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_visible_person_or_404(db, person_id, current_user)
    return db.query(Source).filter(Source.person_id == person_id).all()


@router.post("", response_model=SourceResponse, status_code=201)
def create_source(
    data: SourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    get_visible_person_or_404(db, data.person_id, current_user)
    source = Source(**data.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.patch("/{source_id}", response_model=SourceResponse)
def update_source(
    source_id: int,
    data: SourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(source, field, value)
    db.commit()
    db.refresh(source)
    return source


@router.delete("/{source_id}", status_code=204)
def delete_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    db.delete(source)
    db.commit()
