from copy import deepcopy
from threading import RLock
from uuid import uuid4

from app.domain.enums import AgentRole, DebateStatus, WinningSide
from app.domain.models import (
    DebateRecord,
    DebateResultRecord,
    DebateTurnRecord,
    ErrorDetailRecord,
    utc_now,
)


class InMemoryDebateRepository:
    def __init__(self) -> None:
        self._debates: dict[str, DebateRecord] = {}
        self._lock = RLock()

    def create(self) -> DebateRecord:
        debate_id = f"deb_{uuid4().hex}"
        now = utc_now()
        debate = DebateRecord(
            debate_id=debate_id,
            status=DebateStatus.CREATED,
            created_at=now,
            updated_at=now,
        )
        with self._lock:
            self._debates[debate_id] = debate
        return deepcopy(debate)

    def get(self, debate_id: str) -> DebateRecord | None:
        with self._lock:
            debate = self._debates.get(debate_id)
            return deepcopy(debate) if debate else None

    def list(self, limit: int, status: DebateStatus | None = None) -> list[DebateRecord]:
        with self._lock:
            debates = list(self._debates.values())
        if status is not None:
            debates = [debate for debate in debates if debate.status == status]
        debates.sort(key=lambda debate: debate.created_at, reverse=True)
        return deepcopy(debates[:limit])

    def update_status(self, debate_id: str, status: DebateStatus) -> DebateRecord | None:
        with self._lock:
            debate = self._debates.get(debate_id)
            if debate is None:
                return None
            debate.status = status
            debate.updated_at = utc_now()
            return deepcopy(debate)

    def set_topic_and_starting_side(
        self,
        debate_id: str,
        topic: str,
        starting_side: WinningSide,
    ) -> DebateRecord | None:
        with self._lock:
            debate = self._debates.get(debate_id)
            if debate is None:
                return None
            debate.topic = topic
            debate.starting_side = starting_side
            debate.status = DebateStatus.TOPIC_SELECTED
            debate.updated_at = utc_now()
            return deepcopy(debate)

    def append_turn(
        self,
        debate_id: str,
        agent_role: AgentRole,
        content: str,
    ) -> DebateRecord | None:
        with self._lock:
            debate = self._debates.get(debate_id)
            if debate is None:
                return None
            turn = DebateTurnRecord(
                turn_number=len(debate.turns) + 1,
                agent_role=agent_role,
                content=content,
            )
            debate.turns.append(turn)
            debate.updated_at = utc_now()
            return deepcopy(debate)

    def set_result(
        self,
        debate_id: str,
        winner: WinningSide,
        judge_summary: str,
    ) -> DebateRecord | None:
        with self._lock:
            debate = self._debates.get(debate_id)
            if debate is None:
                return None
            debate.result = DebateResultRecord(winner=winner, judge_summary=judge_summary)
            debate.status = DebateStatus.COMPLETED
            debate.updated_at = utc_now()
            return deepcopy(debate)

    def set_failed(
        self,
        debate_id: str,
        code: str,
        message: str,
        details: dict | None = None,
    ) -> DebateRecord | None:
        with self._lock:
            debate = self._debates.get(debate_id)
            if debate is None:
                return None
            debate.status = DebateStatus.FAILED
            debate.error = ErrorDetailRecord(code=code, message=message, details=details)
            debate.updated_at = utc_now()
            return deepcopy(debate)

    def clear(self) -> None:
        with self._lock:
            self._debates.clear()

