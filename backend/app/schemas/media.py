from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MediaBase(BaseModel):
    person_id: int
    file_url: str
    file_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None


class MediaCreate(MediaBase):
    pass


class MediaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class MediaResponse(MediaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
