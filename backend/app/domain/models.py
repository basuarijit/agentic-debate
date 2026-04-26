from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.enums import AgentRole, DebateStatus, WinningSide


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class DebateTurnRecord:
    turn_number: int
    agent_role: AgentRole
    content: str
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class DebateResultRecord:
    winner: WinningSide
    judge_summary: str
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class ErrorDetailRecord:
    code: str
    message: str
    details: dict | None = None


@dataclass
class DebateRecord:
    debate_id: str
    status: DebateStatus
    topic: str | None = None
    starting_side: WinningSide | None = None
    turns: list[DebateTurnRecord] = field(default_factory=list)
    result: DebateResultRecord | None = None
    error: ErrorDetailRecord | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

