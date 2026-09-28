from __future__ import annotations

import enum
from datetime import UTC, date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _now() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    trees: Mapped[list[Tree]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class Tree(Base):
    __tablename__ = "trees"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    owner: Mapped[User] = relationship(back_populates="trees")
    people: Mapped[list[Person]] = relationship(back_populates="tree", cascade="all, delete-orphan")


class Sex(enum.StrEnum):
    female = "female"
    male = "male"
    unknown = "unknown"


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)
    tree_id: Mapped[int] = mapped_column(ForeignKey("trees.id", ondelete="CASCADE"), index=True)
    given_name: Mapped[str] = mapped_column(String(120))
    family_name: Mapped[str | None] = mapped_column(String(120))
    sex: Mapped[Sex] = mapped_column(Enum(Sex, name="sex"), default=Sex.unknown)
    birth_date: Mapped[date | None] = mapped_column(Date)
    birth_place: Mapped[str | None] = mapped_column(String(200))
    death_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)

    tree: Mapped[Tree] = relationship(back_populates="people")


class RelationKind(enum.StrEnum):
    parent = "parent"  # person_a is a parent of person_b
    spouse = "spouse"  # symmetric; stored once with person_a_id < person_b_id


class Relationship(Base):
    __tablename__ = "relationships"
    __table_args__ = (
        UniqueConstraint("person_a_id", "person_b_id", "kind", name="uq_relationship"),
        CheckConstraint("person_a_id <> person_b_id", name="ck_not_self"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tree_id: Mapped[int] = mapped_column(ForeignKey("trees.id", ondelete="CASCADE"), index=True)
    person_a_id: Mapped[int] = mapped_column(ForeignKey("people.id", ondelete="CASCADE"))
    person_b_id: Mapped[int] = mapped_column(ForeignKey("people.id", ondelete="CASCADE"))
    kind: Mapped[RelationKind] = mapped_column(Enum(RelationKind, name="relation_kind"))
