"""Base service class shared by all pipeline services."""
from sqlalchemy.orm import Session
from app.utils.llm_client import LLMClient
from app.utils.logger import get_logger


class BaseService:
    def __init__(self, db: Session):
        self.db = db
        self.llm = LLMClient()
        self.logger = get_logger(self.__class__.__name__)

    async def run(self, scenario_id: str) -> None:
        raise NotImplementedError
