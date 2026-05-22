from fastapi import HTTPException, UploadFile, status
from app.config import settings

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_GEDCOM_TYPES = {"text/plain", "application/octet-stream", "text/x-gedcom"}
GEDCOM_EXTENSIONS = {".ged", ".gedcom"}


def validate_gedcom_file(file: UploadFile) -> None:
    import os
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in GEDCOM_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension. Allowed: {', '.join(GEDCOM_EXTENSIONS)}",
        )


async def check_gedcom_size(file: UploadFile) -> bytes:
    content = await file.read()
    max_bytes = settings.MAX_GEDCOM_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"GEDCOM file exceeds maximum size of {settings.MAX_GEDCOM_SIZE_MB} MB",
        )
    return content


def validate_image_file(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}",
        )
