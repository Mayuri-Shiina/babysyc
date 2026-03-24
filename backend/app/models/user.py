from typing import Literal

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

UserStatus = Literal["active", "invited", "disabled"]


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    created_families = relationship("Family", back_populates="created_by_user")
    family_memberships = relationship("FamilyMember", back_populates="user")
    sent_invitations = relationship(
        "FamilyInvitation",
        back_populates="invited_by_user",
        foreign_keys="FamilyInvitation.invited_by_user_id",
    )
