from datetime import date, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class GrowthRecord(Base, TimestampMixin):
    __tablename__ = "growth_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    baby_id: Mapped[str] = mapped_column(
        ForeignKey("babies.id"),
        nullable=False,
        index=True,
    )
    record_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    baby = relationship("Baby", back_populates="growth_records")
