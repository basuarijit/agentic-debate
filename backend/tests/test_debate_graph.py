import pytest

from app.orchestration.debate_graph import DebateGraph
from app.orchestration.llm_client import MockDebateLlmClient


@pytest.mark.asyncio
async def test_debate_graph_streams_topic_turns_and_judgment() -> None:
    graph = DebateGraph(MockDebateLlmClient())

    events = []
    async for node_name, node_update in graph.stream():
        events.append((node_name, node_update))

    node_names = [node_name for node_name, _ in events]
    assert node_names[0] == "select_topic"
    assert node_names[-1] == "judge"
    assert node_names.count("pro_turn") == 3
    assert node_names.count("con_turn") == 3

    turn_events = [
        node_update
        for node_name, node_update in events
        if node_name in {"pro_turn", "con_turn"}
    ]
    assert [len(event["turns"]) for event in turn_events] == [1, 2, 3, 4, 5, 6]

