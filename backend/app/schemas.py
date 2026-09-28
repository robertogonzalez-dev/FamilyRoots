from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import RelationKind, Sex


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: str = Field(min_length=1, max_length=120)


class UserOut(ORM):
    id: int
    email: EmailStr
    display_name: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TreeIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None


class TreeOut(ORM):
    id: int
    name: str
    description: str | None


class PersonIn(BaseModel):
    given_name: str = Field(min_length=1, max_length=120)
    family_name: str | None = None
    sex: Sex = Sex.unknown
    birth_date: date | None = None
    birth_place: str | None = None
    death_date: date | None = None
    notes: str | None = None


class PersonOut(ORM, PersonIn):
    id: int


class RelationshipIn(BaseModel):
    person_a_id: int
    person_b_id: int
    kind: RelationKind


class RelationshipOut(ORM, RelationshipIn):
    id: int


class TreeGraph(BaseModel):
    """Nodes + edges, shaped for the frontend tree renderer."""

    people: list[PersonOut]
    relationships: list[RelationshipOut]


class Ancestor(BaseModel):
    person: PersonOut
    generation: int  # 1 = parent, 2 = grandparent, ...
