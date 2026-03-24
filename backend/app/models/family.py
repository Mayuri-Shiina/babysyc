from datetime import datetime
from typing import Literal

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

FamilyMemberRole = Literal["SuperOwner", "Editor", "Viewer"]
FamilyMemberStatus = Literal["active", "invited", "removed"]
InvitationStatus = Literal["pending", "accepted", "expired", "revoked"]


class Family(Base, TimestampMixin):
    __tablename__ = "families"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    current_baby_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    created_by_user = relationship("User", back_populates="created_families")
    members = relationship("FamilyMember", back_populates="family")
    invitations = relationship("FamilyInvitation", back_populates="family")
    babies = relationship("Baby", back_populates="family")


class FamilyMember(Base, TimestampMixin):
    __tablename__ = "family_members"
    __table_args__ = (
        UniqueConstraint("family_id", "user_id", name="uq_family_members_family_user"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    family_id: Mapped[str] = mapped_column(
        ForeignKey("families.id"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    family = relationship("Family", back_populates="members")
    user = relationship("User", back_populates="family_memberships")


class FamilyInvitation(Base, TimestampMixin):
    __tablename__ = "family_invitations"
    __table_args__ = (
        UniqueConstraint("family_id", "invitee_email", name="uq_family_invitations_family_email"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    family_id: Mapped[str] = mapped_column(
        ForeignKey("families.id"),
        nullable=False,
        index=True,
    )
    invited_by_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    invitee_name: Mapped[str] = mapped_column(String(100), nullable=False)
    invitee_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    invite_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    family = relationship("Family", back_populates="invitations")
    invited_by_user = relationship(
        "User",
        back_populates="sent_invitations",
        foreign_keys=[invited_by_user_id],
    )
