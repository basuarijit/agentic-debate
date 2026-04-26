from app.api.schemas import (
    DebateDetail,
    DebateListResponse,
    DebateResult,
    DebateResultResponse,
    DebateSummary,
    DebateTurn,
    DebateTurnsResponse,
    Links,
    StartDebateResponse,
)
from app.core.config import Settings
from app.core.errors import debate_failed, debate_not_completed, debate_not_found
from app.domain.enums import AgentRole, DebateStatus
from app.domain.models import DebateRecord
from app.orchestration.debate_graph import DebateGraph
from app.orchestration.llm_client import build_llm_client
from app.repositories.debate_repository import InMemoryDebateRepository


class DebateService:
    def __init__(self, repository: InMemoryDebateRepository, settings: Settings) -> None:
        self._repository = repository
        self._settings = settings

    def start_debate(self) -> StartDebateResponse:
        debate = self._repository.create()
        return StartDebateResponse(
            debate_id=debate.debate_id,
            status=debate.status,
            topic=debate.topic,
            starting_side=debate.starting_side,
            created_at=debate.created_at,
            updated_at=debate.updated_at,
            links=Links(self=f"{self._settings.api_v1_prefix}/debates/{debate.debate_id}"),
        )

    async def run_debate(self, debate_id: str) -> None:
        debate = self._repository.get(debate_id)
        if debate is None:
            return

        try:
            llm_client = build_llm_client(self._settings)
            graph = DebateGraph(llm_client)
            final_state = await graph.run()

            topic = final_state["topic"]
            starting_side = final_state["starting_side"]
            winner = final_state["winner"]
            judge_summary = final_state["judge_summary"]
            if not topic or not starting_side or not winner or not judge_summary:
                raise ValueError("Debate graph completed without required final state.")

            self._repository.set_topic_and_starting_side(
                debate_id=debate_id,
                topic=topic,
                starting_side=starting_side,
            )
            self._repository.update_status(debate_id, DebateStatus.IN_PROGRESS)

            for turn in final_state["turns"]:
                self._repository.append_turn(
                    debate_id=debate_id,
                    agent_role=turn["agent_role"],
                    content=turn["content"],
                )

            self._repository.update_status(debate_id, DebateStatus.JUDGING)
            self._repository.set_result(
                debate_id=debate_id,
                winner=winner,
                judge_summary=judge_summary,
            )
        except Exception as exc:
            self._repository.set_failed(
                debate_id=debate_id,
                code="MODEL_PROVIDER_ERROR",
                message="Debate orchestration failed.",
                details={"reason": str(exc)},
            )

    def get_debate(self, debate_id: str) -> DebateDetail:
        debate = self._get_existing_debate(debate_id)
        return self._to_detail(debate)

    def list_debates(
        self,
        limit: int,
        status: DebateStatus | None = None,
    ) -> DebateListResponse:
        debates = self._repository.list(limit=limit, status=status)
        items = [self._to_summary(debate) for debate in debates]
        return DebateListResponse(items=items, limit=limit, count=len(items))

    def get_turns(self, debate_id: str) -> DebateTurnsResponse:
        debate = self._get_existing_debate(debate_id)
        return DebateTurnsResponse(
            debate_id=debate.debate_id,
            topic=debate.topic,
            turns=[self._to_turn(turn) for turn in debate.turns],
        )

    def get_result(self, debate_id: str) -> DebateResultResponse:
        debate = self._get_existing_debate(debate_id)
        if debate.status == DebateStatus.FAILED:
            raise debate_failed(debate_id)
        if debate.status != DebateStatus.COMPLETED or debate.result is None:
            raise debate_not_completed(debate_id, debate.status.value)
        return DebateResultResponse(
            debate_id=debate.debate_id,
            status=debate.status,
            result=self._to_result(debate.result),
        )

    def _get_existing_debate(self, debate_id: str) -> DebateRecord:
        debate = self._repository.get(debate_id)
        if debate is None:
            raise debate_not_found(debate_id)
        return debate

    def _to_detail(self, debate: DebateRecord) -> DebateDetail:
        return DebateDetail(
            debate_id=debate.debate_id,
            status=debate.status,
            topic=debate.topic,
            starting_side=debate.starting_side,
            created_at=debate.created_at,
            updated_at=debate.updated_at,
            turns=[self._to_turn(turn) for turn in debate.turns],
            result=self._to_result(debate.result) if debate.result else None,
            error=debate.error,
        )

    def _to_summary(self, debate: DebateRecord) -> DebateSummary:
        return DebateSummary(
            debate_id=debate.debate_id,
            status=debate.status,
            topic=debate.topic,
            starting_side=debate.starting_side,
            created_at=debate.created_at,
            updated_at=debate.updated_at,
            result=self._to_result(debate.result) if debate.result else None,
        )

    def _to_turn(self, turn) -> DebateTurn:
        return DebateTurn(
            turn_number=turn.turn_number,
            agent_role=AgentRole(turn.agent_role),
            content=turn.content,
            created_at=turn.created_at,
        )

    def _to_result(self, result) -> DebateResult:
        return DebateResult(
            winner=result.winner,
            judge_summary=result.judge_summary,
            created_at=result.created_at,
        )

