from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.database.models import TokenType


class TokenCreate(BaseModel):
    name: str = Field(..., max_length=160)
    token_type: TokenType
    plant_location: str | None = Field(None, max_length=400)
    description: str | None = None
    sensitivity: int | None = Field(None, ge=1, le=10)


class TokenOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trigger_id: str
    name: str
    token_type: str
    plant_location: str | None
    description: str | None
    sensitivity: int
    artifact: dict
    callback_url: str
    is_active: bool
    trigger_count: int
    first_triggered_at: datetime | None
    last_triggered_at: datetime | None
    created_at: datetime


class TriggerEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    token_id: int
    source_ip: str
    user_agent: str | None
    method: str
    path: str
    referer: str | None
    channel: str
    severity: str
    threat_score: int
    occurred_at: datetime