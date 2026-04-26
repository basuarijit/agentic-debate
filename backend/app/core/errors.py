from fastapi import status


class AppException(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


def debate_not_found(debate_id: str) -> AppException:
    return AppException(
        status_code=status.HTTP_404_NOT_FOUND,
        code="DEBATE_NOT_FOUND",
        message="Debate was not found.",
        details={"debate_id": debate_id},
    )


def debate_not_completed(debate_id: str, current_status: str) -> AppException:
    return AppException(
        status_code=status.HTTP_409_CONFLICT,
        code="DEBATE_NOT_COMPLETED",
        message="Debate result is not available until judging is complete.",
        details={"debate_id": debate_id, "status": current_status},
    )


def debate_failed(debate_id: str) -> AppException:
    return AppException(
        status_code=status.HTTP_409_CONFLICT,
        code="DEBATE_FAILED",
        message="Debate failed during orchestration.",
        details={"debate_id": debate_id},
    )

