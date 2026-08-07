from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import ForeignKey, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class DecoyType(str, Enum):
    SSH = "ssh"
    HTTP = "http"
    DATABASE = "database"
    SMB = "smb"
    FILE_SHARE = "file_share"


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Decoy(Base):
    """A deployed deception asset (honeypot/honeytoken)."""
    __tablename__ = "decoys"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    decoy_type: Mapped[str] = mapped_column(String(32), index=True)
    listen_host: Mapped[str] = mapped_column(String(64), default="0.0.0.0")
    listen_port: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(default=True)
    profile: Mapped[dict] = mapped_column(JSON, default=dict)  # banner, fake fs, creds
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    interactions: Mapped[list["Interaction"]] = relationship(
        back_populates="decoy", cascade="all, delete-orphan"
    )


class Attacker(Base):
    """An observed adversary, keyed by source identity."""
    __tablename__ = "attackers"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_ip: Mapped[str] = mapped_column(String(45), unique=True, index=True)
    threat_score: Mapped[int] = mapped_column(Integer, default=0, index=True)
    fingerprint: Mapped[dict] = mapped_column(JSON, default=dict)  # ua, tooling, ttps
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    interactions: Mapped[list["Interaction"]] = relationship(back_populates="attacker")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="attacker")


class Interaction(Base):
    """A single logged touch against a decoy."""
    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    decoy_id: Mapped[int] = mapped_column(ForeignKey("decoys.id", ondelete="CASCADE"))
    attacker_id: Mapped[int] = mapped_column(ForeignKey("attackers.id"))
    protocol: Mapped[str] = mapped_column(String(32))
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )

    decoy: Mapped[Decoy] = relationship(back_populates="interactions")
    attacker: Mapped[Attacker] = relationship(back_populates="interactions")


class Alert(Base):
    """Detection output requiring analyst attention or auto-response."""
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    attacker_id: Mapped[int | None] = mapped_column(
        ForeignKey("attackers.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(200))
    severity: Mapped[str] = mapped_column(String(16), index=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    acknowledged: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )

    attacker: Mapped[Attacker | None] = relationship(back_populates="alerts")