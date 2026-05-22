import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.media import Media
from app.schemas.media import MediaResponse, MediaUpdate
from app.auth.dependencies import get_current_user, require_editor
from app.models.user import User
from app.config import settings
from app.utils.file_validation import validate_image_file

router = APIRouter()


@router.get("/person/{person_id}", response_model=list[MediaResponse])
def list_person_media(
    person_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Media).filter(Media.person_id == person_id).all()


@router.post("/person/{person_id}", response_model=MediaResponse, status_code=201)
async def upload_media(
    person_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    validate_image_file(file)
    ext = os.path.splitext(file.filename or "")[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    person_dir = os.path.join(settings.UPLOAD_DIR, str(person_id))
    os.makedirs(person_dir, exist_ok=True)
    filepath = os.path.join(person_dir, filename)
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)
    file_url = f"/uploads/{person_id}/{filename}"
    media = Media(
        person_id=person_id,
        file_url=file_url,
        file_type=file.content_type,
        title=file.filename,
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media


@router.patch("/{media_id}", response_model=MediaResponse)
def update_media(
    media_id: int,
    data: MediaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(media, field, value)
    db.commit()
    db.refresh(media)
    return media


@router.delete("/{media_id}", status_code=204)
def delete_media(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor),
):
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    db.delete(media)
    db.commit()
