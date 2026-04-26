from app.core.config import get_settings
from app.repositories.debate_repository import InMemoryDebateRepository
from app.services.debate_service import DebateService


repository = InMemoryDebateRepository()


def get_debate_service() -> DebateService:
    return DebateService(repository=repository, settings=get_settings())

