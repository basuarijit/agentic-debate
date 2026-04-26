# Backend

Backend API for the debate application.

Stack:

- Python
- FastAPI
- Uvicorn
- OpenAI
- LangChain
- LangGraph

## Local Setup

```powershell
cd backend
uv venv
uv sync --all-groups
Copy-Item .env.example .env
uv run uvicorn app.main:app --reload
```

Open FastAPI docs:

```text
http://127.0.0.1:8000/docs
```

## LLM Provider

The default `DEBATE_LLM_PROVIDER=mock` lets you manually test the APIs without an OpenAI key.

To use OpenAI through LangChain:

```text
DEBATE_LLM_PROVIDER=openai
OPENAI_API_KEY=<your-api-key>
OPENAI_MODEL=gpt-4o-mini
```

## Main API Paths

- `GET /api/v1/health`
- `POST /api/v1/debates`
- `GET /api/v1/debates`
- `GET /api/v1/debates/{debate_id}`
- `GET /api/v1/debates/{debate_id}/turns`
- `GET /api/v1/debates/{debate_id}/result`

## Tests

```powershell
cd backend
uv run pytest
```
