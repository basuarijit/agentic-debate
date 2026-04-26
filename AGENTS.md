# AGENTS.md

## Project Mission

Build an AI-agent debate application from the supplied Business Requirements Document (BRD), following Agile SDLC and DevSecOps practices.

The application will support a structured debate process between AI agents. The implementation stack is:

- UI: React with npm
- Backend: Python
- App server: Uvicorn
- API framework: FastAPI
- AI models: OpenAI
- Agent and RAG orchestration: LangChain / LangGraph
- DevSecOps: GitHub and GitHub Actions

## Repository Shape

The project must keep two high-level application directories:

- `backend/` for Python, FastAPI, LangChain/LangGraph, OpenAI integration, tests, and backend deployment assets.
- `frontend/` for React/npm UI source, tests, and frontend deployment assets.

Supporting project artefacts live outside those directories:

- `docs/` for SDLC artefacts, architecture, decisions, and operating notes.
- `.github/` for GitHub templates and future GitHub Actions workflows.

## SDLC Workflow

Do not skip SDLC stages. Work in this order unless the user explicitly changes it:

1. BRD intake and clarification.
2. Agile planning: epics, user stories, acceptance criteria, and backlog.
3. Test planning: test cases, traceability, and quality gates.
4. Design: architecture, API design, data design, agent workflow design, security design, and deployment design.
5. Implementation: backend code, frontend code, tests, and automation.
6. Verification: unit tests, integration tests, security checks, and release readiness.
7. Deployment: CI/CD, environment configuration, deployment runbooks, and monitoring notes.

For this initial scaffold, do not create stage-specific deliverables such as epics, user stories, test cases, detailed designs, or source code. Create those only when the user asks for that SDLC step.

## Working Rules For Codex

- Read the BRD before generating SDLC artefacts.
- Keep generated artefacts traceable to the BRD.
- Ask concise clarification questions when a requirement is ambiguous or risky.
- Keep backend and frontend changes separated by directory.
- Prefer existing project conventions once code exists.
- Do not commit secrets, API keys, tokens, credentials, or private endpoint values.
- Use `.env.example` files for required environment variable names only.
- Add tests alongside implementation during the coding stage.
- Update documentation when making architectural, security, deployment, or operating changes.

## DevSecOps Expectations

Future implementation should include:

- CI checks for formatting, linting, tests, dependency review, and security scanning.
- Secret scanning and dependency vulnerability checks.
- Separate environment configuration for local, test, staging, and production.
- Least-privilege handling of OpenAI and platform credentials.
- Release notes and deployment approval gates where appropriate.

Do not add active deployment workflows until the application structure and commands are defined.

