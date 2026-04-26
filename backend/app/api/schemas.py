from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import AgentRole, DebateMode, DebateStatus, WinningSide


class HealthResponse(BaseModel):
    status: str
    service: str


class Links(BaseModel):
    self: str


class StartDebateRequest(BaseModel):
    mode: DebateMode = DebateMode.AUTOMATIC


class StartDebateResponse(BaseModel):
    debate_id: str
    status: DebateStatus
    topic: str | None
    starting_side: WinningSide | None
    created_at: datetime
    updated_at: datetime
    links: Links


class DebateTurn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    turn_number: int = Field(ge=1)
    agent_role: AgentRole
    content: str
    created_at: datetime


class DebateResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    winner: WinningSide
    judge_summary: str
    created_at: datetime


class ErrorDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    message: str
    details: dict | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class DebateSummary(BaseModel):
    debate_id: str
    status: DebateStatus
    topic: str | None
    starting_side: WinningSide | None
    created_at: datetime
    updated_at: datetime
    result: DebateResult | None = None


class DebateDetail(BaseModel):
    debate_id: str
    status: DebateStatus
    topic: str | None
    starting_side: WinningSide | None
    created_at: datetime
    updated_at: datetime
    turns: list[DebateTurn]
    result: DebateResult | None
    error: ErrorDetail | None


class DebateListResponse(BaseModel):
    items: list[DebateSummary]
    limit: int
    count: int


class DebateTurnsResponse(BaseModel):
    debate_id: str
    topic: str | None
    turns: list[DebateTurn]


class DebateResultResponse(BaseModel):
    debate_id: str
    status: DebateStatus
    result: DebateResult

