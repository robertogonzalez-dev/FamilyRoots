from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel
from app.models.person import Gender


class PersonBase(BaseModel):
    external_id: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    maiden_name: Optional[str] = None
    gender: Gender = Gender.unknown
    birth_date: Optional[date] = None
    birth_place: Optional[str] = None
    death_date: Optional[date] = None
    death_place: Optional[str] = None
    biography: Optional[str] = None
    is_living: bool = True
    profile_photo_url: Optional[str] = None


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    maiden_name: Optional[str] = None
    gender: Optional[Gender] = None
    birth_date: Optional[date] = None
    birth_place: Optional[str] = None
    death_date: Optional[date] = None
    death_place: Optional[str] = None
    biography: Optional[str] = None
    is_living: Optional[bool] = None
    profile_photo_url: Optional[str] = None


class PersonResponse(PersonBase):
    id: int
    full_name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PersonSummary(BaseModel):
    id: int
    full_name: str
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    gender: Gender
    is_living: bool
    profile_photo_url: Optional[str] = None

    model_config = {"from_attributes": True}
