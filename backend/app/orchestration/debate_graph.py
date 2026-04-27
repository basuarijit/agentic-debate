import random
from collections.abc import AsyncIterator
from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.domain.enums import AgentRole, WinningSide
from app.orchestration.llm_client import DebateLlmClient


class DebateGraphState(TypedDict):
    topic: str | None
    starting_side: WinningSide | None
    current_side: AgentRole | None
    pro_turn_count: int
    con_turn_count: int
    turns: list[dict]
    winner: WinningSide | None
    judge_summary: str | None


class DebateGraph:
    def __init__(self, llm_client: DebateLlmClient) -> None:
        self._llm_client = llm_client
        self._graph = self._build_graph()

    async def run(self) -> DebateGraphState:
        initial_state: DebateGraphState = {
            "topic": None,
            "starting_side": None,
            "current_side": None,
            "pro_turn_count": 0,
            "con_turn_count": 0,
            "turns": [],
            "winner": None,
            "judge_summary": None,
        }
        return await self._graph.ainvoke(initial_state)

    async def stream(self) -> AsyncIterator[tuple[str, dict]]:
        initial_state: DebateGraphState = {
            "topic": None,
            "starting_side": None,
            "current_side": None,
            "pro_turn_count": 0,
            "con_turn_count": 0,
            "turns": [],
            "winner": None,
            "judge_summary": None,
        }
        async for event in self._graph.astream(initial_state, stream_mode="updates"):
            for node_name, node_update in event.items():
                yield node_name, node_update

    def _build_graph(self):
        graph = StateGraph(DebateGraphState)
        graph.add_node("select_topic", self._select_topic)
        graph.add_node("pro_turn", self._pro_turn)
        graph.add_node("con_turn", self._con_turn)
        graph.add_node("judge", self._judge)

        graph.set_entry_point("select_topic")
        graph.add_conditional_edges(
            "select_topic",
            self._route_to_starting_side,
            {"pro": "pro_turn", "con": "con_turn"},
        )
        graph.add_conditional_edges(
            "pro_turn",
            self._route_after_turn,
            {"pro": "pro_turn", "con": "con_turn", "judge": "judge"},
        )
        graph.add_conditional_edges(
            "con_turn",
            self._route_after_turn,
            {"pro": "pro_turn", "con": "con_turn", "judge": "judge"},
        )
        graph.add_edge("judge", END)
        return graph.compile()

    async def _select_topic(self, state: DebateGraphState) -> dict:
        topic = await self._llm_client.select_topic()
        starting_role = random.choice([AgentRole.PRO, AgentRole.CON])
        starting_side = WinningSide(starting_role.value)
        return {
            "topic": topic,
            "starting_side": starting_side,
            "current_side": starting_role,
        }

    async def _pro_turn(self, state: DebateGraphState) -> dict:
        return await self._create_turn(state, AgentRole.PRO)

    async def _con_turn(self, state: DebateGraphState) -> dict:
        return await self._create_turn(state, AgentRole.CON)

    async def _create_turn(self, state: DebateGraphState, role: AgentRole) -> dict:
        turn_index = (
            state["pro_turn_count"] + 1
            if role == AgentRole.PRO
            else state["con_turn_count"] + 1
        )
        content = await self._llm_client.create_argument(
            topic=state["topic"] or "",
            role=role,
            turn_index=turn_index,
            prior_turns=state["turns"],
        )
        turns = [
            *state["turns"],
            {
                "turn_number": len(state["turns"]) + 1,
                "agent_role": role,
                "content": content,
            },
        ]
        if role == AgentRole.PRO:
            return {
                "turns": turns,
                "pro_turn_count": state["pro_turn_count"] + 1,
                "current_side": AgentRole.CON,
            }
        return {
            "turns": turns,
            "con_turn_count": state["con_turn_count"] + 1,
            "current_side": AgentRole.PRO,
        }

    async def _judge(self, state: DebateGraphState) -> dict:
        winner, judge_summary = await self._llm_client.judge(
            topic=state["topic"] or "",
            turns=state["turns"],
        )
        return {"winner": winner, "judge_summary": judge_summary}

    def _route_to_starting_side(self, state: DebateGraphState) -> str:
        if state["starting_side"] == WinningSide.PRO:
            return "pro"
        return "con"

    def _route_after_turn(self, state: DebateGraphState) -> str:
        if state["pro_turn_count"] >= 3 and state["con_turn_count"] >= 3:
            return "judge"
        next_side = state["current_side"]
        if next_side == AgentRole.PRO and state["pro_turn_count"] < 3:
            return "pro"
        if next_side == AgentRole.CON and state["con_turn_count"] < 3:
            return "con"
        if state["pro_turn_count"] < 3:
            return "pro"
        return "con"
