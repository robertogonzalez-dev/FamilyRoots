from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from app.models.relationship import RelationshipType


class RelationshipBase(BaseModel):
    person1_id: int
    person2_id: int
    relationship_type: RelationshipType
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None


class RelationshipCreate(RelationshipBase):
    pass


class RelationshipUpdate(BaseModel):
    relationship_type: Optional[RelationshipType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None


class RelationshipResponse(RelationshipBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
