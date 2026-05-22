from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SourceBase(BaseModel):
    person_id: int
    title: Optional[str] = None
    citation: Optional[str] = None
    source_url: Optional[str] = None
    notes: Optional[str] = None


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    title: Optional[str] = None
    citation: Optional[str] = None
    source_url: Optional[str] = None
    notes: Optional[str] = None


class SourceResponse(SourceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
