from enum import StrEnum


class DebateStatus(StrEnum):
    CREATED = "created"
    TOPIC_SELECTED = "topic_selected"
    IN_PROGRESS = "in_progress"
    JUDGING = "judging"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentRole(StrEnum):
    TOPIC_SELECTOR = "topic_selector"
    PRO = "pro"
    CON = "con"
    JUDGE = "judge"


class WinningSide(StrEnum):
    PRO = "pro"
    CON = "con"


class DebateMode(StrEnum):
    AUTOMATIC = "automatic"

