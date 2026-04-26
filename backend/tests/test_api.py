from fastapi.testclient import TestClient

from app.dependencies import repository
from app.main import app


client = TestClient(app)


def setup_function() -> None:
    repository.clear()


def test_health_check() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "agentic-debate-api"}


def test_start_debate_runs_mock_orchestration() -> None:
    response = client.post("/api/v1/debates", json={"mode": "automatic"})

    assert response.status_code == 202
    payload = response.json()
    debate_id = payload["debate_id"]

    detail_response = client.get(f"/api/v1/debates/{debate_id}")
    assert detail_response.status_code == 200

    detail = detail_response.json()
    assert detail["status"] == "completed"
    assert detail["topic"] == "Should AI agents be used for formal debate training?"
    assert detail["starting_side"] in {"pro", "con"}
    assert len(detail["turns"]) == 6
    assert detail["result"]["winner"] in {"pro", "con"}

    pro_turns = [
        turn for turn in detail["turns"] if turn["agent_role"] == "pro"
    ]
    con_turns = [
        turn for turn in detail["turns"] if turn["agent_role"] == "con"
    ]
    assert len(pro_turns) == 3
    assert len(con_turns) == 3


def test_get_debate_result() -> None:
    create_response = client.post("/api/v1/debates", json={"mode": "automatic"})
    debate_id = create_response.json()["debate_id"]

    response = client.get(f"/api/v1/debates/{debate_id}/result")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["result"]["winner"] in {"pro", "con"}


def test_list_debates() -> None:
    client.post("/api/v1/debates", json={"mode": "automatic"})
    client.post("/api/v1/debates", json={"mode": "automatic"})

    response = client.get("/api/v1/debates?limit=10")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 2
    assert len(payload["items"]) == 2


def test_debate_not_found() -> None:
    response = client.get("/api/v1/debates/deb_missing")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DEBATE_NOT_FOUND"

