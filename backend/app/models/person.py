import enum
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Gender(str, enum.Enum):
    male = "male"
    female = "female"
    unknown = "unknown"
    other = "other"


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    maiden_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    gender: Mapped[Gender] = mapped_column(Enum(Gender), default=Gender.unknown, nullable=False)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    birth_place: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    death_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    death_place: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    biography: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_living: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    profile_photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    media = relationship("Media", back_populates="person", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="person", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="person", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(p for p in parts if p)
