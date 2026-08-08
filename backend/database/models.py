from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import ForeignKey, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Boolean

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

class AttackLog(Base):
    """Raw log of an attack event against a decoy."""
    __tablename__ = "attack_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_ip: Mapped[str] = mapped_column(String(45), index=True)
    target_port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    decoy_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    protocol: Mapped[str] = mapped_column(String(32), default="http")
    method: Mapped[str | None] = mapped_column(String(16), nullable=True)
    path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    threat_score: Mapped[int] = mapped_column(Integer, default=0, index=True)
    severity: Mapped[str] = mapped_column(String(16), default=Severity.INFO.value)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )  

class TokenType(str, Enum):
    AWS_KEY = "aws_key"
    GCP_KEY = "gcp_key"
    AZURE_KEY = "azure_key"
    DB_CONNECTION = "db_connection"
    API_KEY = "api_key"
    SSH_KEY = "ssh_key"
    ENV_FILE = "env_file"
    DOCUMENT = "document"
    S3_BUCKET = "s3_bucket"
    K8S_SECRET = "k8s_secret"
    SOURCE_SECRET = "source_secret"
    CANARY_URL = "canary_url"
    FAKE_USER = "fake_user"


class Honeytoken(Base):
    """A single planted bait artifact with a unique callback identity."""
    __tablename__ = "honeytokens"

    id: Mapped[int] = mapped_column(primary_key=True)

    # short, URL-safe id embedded in the artifact
    trigger_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)

    name: Mapped[str] = mapped_column(String(160))
    token_type: Mapped[str] = mapped_column(String(32), index=True)

    # where this token was planted, e.g. "gitlab:infra-repo/config/prod.env"
    plant_location: Mapped[str | None] = mapped_column(String(400), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 1-10; feeds threat scoring. A prod DB string outranks a test API key.
    sensitivity: Mapped[int] = mapped_column(Integer, default=5)

    # the generated fake artifact (key pair, conn string, file body...)
    artifact: Mapped[dict] = mapped_column(JSON, default=dict)

    callback_url: Mapped[str] = mapped_column(String(400))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    trigger_count: Mapped[int] = mapped_column(Integer, default=0, index=True)
    first_triggered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_triggered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )

    events: Mapped[list["TriggerEvent"]] = relationship(
        back_populates="token", cascade="all, delete-orphan"
    )


class TriggerEvent(Base):
    """One observed interaction with a honeytoken."""
    __tablename__ = "trigger_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    token_id: Mapped[int] = mapped_column(
        ForeignKey("honeytokens.id", ondelete="CASCADE"), index=True
    )

    source_ip: Mapped[str] = mapped_column(String(45), index=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    method: Mapped[str] = mapped_column(String(10), default="GET")
    path: Mapped[str] = mapped_column(String(512))
    referer: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # how the callback arrived: http, dns, smtp...
    channel: Mapped[str] = mapped_column(String(24), default="http")

    headers: Mapped[dict] = mapped_column(JSON, default=dict)
    query: Mapped[dict] = mapped_column(JSON, default=dict)
    body_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)

    severity: Mapped[str] = mapped_column(String(16), default=Severity.HIGH.value)
    threat_score: Mapped[int] = mapped_column(Integer, default=0, index=True)

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )

    token: Mapped[Honeytoken] = relationship(back_populates="events")  

class ActionType(str, Enum):
    BLOCK_IP = "block_ip"
    REVOKE_SESSION = "revoke_session"
    QUARANTINE_HOST = "quarantine_host"
    ESCALATE_ALERT = "escalate_alert"
    DISABLE_ACCOUNT = "disable_account"

class ContainmentAction(Base):
    """Audit log of autonomous actions taken against an attacker."""
    __tablename__ = "containment_actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("trigger_events.id"), index=True)
    token_id: Mapped[int] = mapped_column(ForeignKey("honeytokens.id"), index=True)
    
    action_type: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16), default="executed") # executed, dry_run, failed
    details: Mapped[dict] = mapped_column(JSON, default=dict)

    attacker_ip: Mapped[str] = mapped_column(String(45), index=True)
    action_type: Mapped[str] = mapped_column(String(50)) # e.g., 'block_ip', 
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    