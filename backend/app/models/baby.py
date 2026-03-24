from datetime import date

from sqlalchemy import Date, ForeignKey, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Baby(Base, TimestampMixin):
    __tablename__ = "babies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    family_id: Mapped[str] = mapped_column(
        ForeignKey("families.id"),
        nullable=False,
        index=True,
    )
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    birth_time: Mapped[str | None] = mapped_column(String(10), nullable=True)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    birth_place: Mapped[str | None] = mapped_column(String(255), nullable=True)
    birth_height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    birth_weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    family = relationship("Family", back_populates="babies")
    growth_records = relationship("GrowthRecord", back_populates="baby")
    media_assets = relationship("MediaAsset", back_populates="baby")
