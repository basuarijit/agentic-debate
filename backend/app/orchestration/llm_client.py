import json
from abc import ABC, abstractmethod

from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import Settings
from app.domain.enums import AgentRole, WinningSide


class DebateLlmClient(ABC):
    @abstractmethod
    async def select_topic(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def create_argument(
        self,
        topic: str,
        role: AgentRole,
        turn_index: int,
        prior_turns: list[dict],
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    async def judge(self, topic: str, turns: list[dict]) -> tuple[WinningSide, str]:
        raise NotImplementedError


class MockDebateLlmClient(DebateLlmClient):
    async def select_topic(self) -> str:
        return "Should AI agents be used for formal debate training?"

    async def create_argument(
        self,
        topic: str,
        role: AgentRole,
        turn_index: int,
        prior_turns: list[dict],
    ) -> str:
        side = "in favor of" if role == AgentRole.PRO else "against"
        return (
            f"Turn {turn_index}: I argue {side} the topic '{topic}'. "
            "This position is supported by clear reasoning, practical impact, "
            "and the need to evaluate both benefits and risks carefully."
        )

    async def judge(self, topic: str, turns: list[dict]) -> tuple[WinningSide, str]:
        pro_word_count = sum(
            len(turn["content"].split())
            for turn in turns
            if turn["agent_role"] == AgentRole.PRO
        )
        con_word_count = sum(
            len(turn["content"].split())
            for turn in turns
            if turn["agent_role"] == AgentRole.CON
        )
        winner = WinningSide.PRO if pro_word_count >= con_word_count else WinningSide.CON
        return (
            winner,
            f"The {winner.value} side won based on clarity, completeness, and structure.",
        )


class OpenAIDebateLlmClient(DebateLlmClient):
    def __init__(self, settings: Settings) -> None:
        from langchain_openai import ChatOpenAI

        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY must be configured when DEBATE_LLM_PROVIDER=openai."
            )

        self._chat = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key,
        )

    async def select_topic(self) -> str:
        response = await self._chat.ainvoke(
            [
                SystemMessage(
                    content=(
                        "You are a debate-topic-selector agent. Select exactly one "
                        "clear, balanced topic for a short structured debate."
                    )
                ),
                HumanMessage(content="Return only the debate topic. Do not add commentary."),
            ]
        )
        return str(response.content).strip().strip('"')

    async def create_argument(
        self,
        topic: str,
        role: AgentRole,
        turn_index: int,
        prior_turns: list[dict],
    ) -> str:
        position = "in favor of" if role == AgentRole.PRO else "against"
        response = await self._chat.ainvoke(
            [
                SystemMessage(
                    content=(
                        f"You are the {role.value} debate agent. Argue {position} "
                        "the topic. Be concise, persuasive, and avoid repeating "
                        "earlier turns."
                    )
                ),
                HumanMessage(
                    content=(
                        f"Topic: {topic}\n"
                        f"Your speaking turn number for this side: {turn_index}\n"
                        f"Prior turns: {prior_turns}\n\n"
                        "Return only your argument text."
                    )
                ),
            ]
        )
        return str(response.content).strip()

    async def judge(self, topic: str, turns: list[dict]) -> tuple[WinningSide, str]:
        response = await self._chat.ainvoke(
            [
                SystemMessage(
                    content=(
                        "You are the judge agent. Decide the debate winner. "
                        "Return strict JSON only with keys winner and judge_summary. "
                        "winner must be either pro or con."
                    )
                ),
                HumanMessage(content=f"Topic: {topic}\nTurns: {turns}"),
            ]
        )
        raw_content = str(response.content).strip()
        try:
            payload = json.loads(raw_content)
            winner = WinningSide(payload["winner"])
            summary = str(payload["judge_summary"]).strip()
            return winner, summary
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            raise ValueError(f"Judge agent returned invalid result: {raw_content}") from exc


def build_llm_client(settings: Settings) -> DebateLlmClient:
    provider = settings.debate_llm_provider.lower()
    if provider == "openai":
        return OpenAIDebateLlmClient(settings)
    if provider == "mock":
        return MockDebateLlmClient()
    raise ValueError("DEBATE_LLM_PROVIDER must be either 'mock' or 'openai'.")
