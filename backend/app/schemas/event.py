from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


class EventBase(BaseModel):
    person_id: int
    event_type: Optional[str] = None
    event_date: Optional[date] = None
    event_place: Optional[str] = None
    description: Optional[str] = None
    source_id: Optional[int] = None


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    event_type: Optional[str] = None
    event_date: Optional[date] = None
    event_place: Optional[str] = None
    description: Optional[str] = None
    source_id: Optional[int] = None


class EventResponse(EventBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
