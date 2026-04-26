from fastapi import APIRouter, BackgroundTasks, Body, Depends, Query, status

from app.api.schemas import (
    DebateDetail,
    DebateListResponse,
    DebateResultResponse,
    DebateTurnsResponse,
    HealthResponse,
    StartDebateRequest,
    StartDebateResponse,
)
from app.core.config import get_settings
from app.domain.enums import DebateStatus
from app.services.debate_service import DebateService
from app.dependencies import get_debate_service


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", service=settings.service_name)


@router.post(
    "/debates",
    response_model=StartDebateResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_debate(
    background_tasks: BackgroundTasks,
    payload: StartDebateRequest = Body(default_factory=StartDebateRequest),
    service: DebateService = Depends(get_debate_service),
) -> StartDebateResponse:
    debate = service.start_debate()
    background_tasks.add_task(service.run_debate, debate.debate_id)
    return debate


@router.get("/debates", response_model=DebateListResponse)
async def list_debates(
    limit: int = Query(default=20, ge=1, le=100),
    status_filter: DebateStatus | None = Query(default=None, alias="status"),
    service: DebateService = Depends(get_debate_service),
) -> DebateListResponse:
    return service.list_debates(limit=limit, status=status_filter)


@router.get("/debates/{debate_id}", response_model=DebateDetail)
async def get_debate(
    debate_id: str,
    service: DebateService = Depends(get_debate_service),
) -> DebateDetail:
    return service.get_debate(debate_id)


@router.get("/debates/{debate_id}/turns", response_model=DebateTurnsResponse)
async def get_debate_turns(
    debate_id: str,
    service: DebateService = Depends(get_debate_service),
) -> DebateTurnsResponse:
    return service.get_turns(debate_id)


@router.get("/debates/{debate_id}/result", response_model=DebateResultResponse)
async def get_debate_result(
    debate_id: str,
    service: DebateService = Depends(get_debate_service),
) -> DebateResultResponse:
    return service.get_result(debate_id)

