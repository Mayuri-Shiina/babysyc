from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class VaccinePlan(Base, TimestampMixin):
    __tablename__ = "vaccine_plans"
    __table_args__ = (
        UniqueConstraint("baby_id", "vaccine_code", "scheduled_date", name="uq_vaccine_plans_baby_code_date"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    family_id: Mapped[str] = mapped_column(
        ForeignKey("families.id"),
        nullable=False,
        index=True,
    )
    baby_id: Mapped[str] = mapped_column(
        ForeignKey("babies.id"),
        nullable=False,
        index=True,
    )
    vaccine_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    vaccine_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dose_label: Mapped[str] = mapped_column(String(50), nullable=False)
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_custom: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    baby = relationship("Baby")
    family = relationship("Family")
    records = relationship("VaccineRecord", back_populates="plan")


class VaccineRecord(Base, TimestampMixin):
    __tablename__ = "vaccine_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    plan_id: Mapped[str] = mapped_column(
        ForeignKey("vaccine_plans.id"),
        nullable=False,
        index=True,
    )
    family_id: Mapped[str] = mapped_column(
        ForeignKey("families.id"),
        nullable=False,
        index=True,
    )
    baby_id: Mapped[str] = mapped_column(
        ForeignKey("babies.id"),
        nullable=False,
        index=True,
    )
    recorded_by_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    administered_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="completed")
    provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    plan = relationship("VaccinePlan", back_populates="records")
    baby = relationship("Baby")
    family = relationship("Family")
    recorded_by_user = relationship("User")
