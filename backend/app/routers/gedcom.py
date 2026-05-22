from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import require_admin
from app.models.user import User
from app.services.gedcom_importer import import_gedcom
from app.utils.file_validation import validate_gedcom_file, check_gedcom_size

router = APIRouter()


@router.post("/import")
async def gedcom_import(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    validate_gedcom_file(file)
    content = await check_gedcom_size(file)
    result = import_gedcom(db, content)
    return {"message": "Import complete", "result": result}
