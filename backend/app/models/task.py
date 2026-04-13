"""Async task tracking — mirrors MiroFish's task model pattern."""
import enum
import json

from sqlalchemy import Text, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, new_uuid, utcnow


class TaskStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    scenario_id: Mapped[str | None] = mapped_column(ForeignKey("scenarios.id", ondelete="CASCADE"))
    task_type: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(SAEnum(TaskStatus), default=TaskStatus.pending)
    progress: Mapped[int] = mapped_column(default=0)
    message: Mapped[str | None] = mapped_column(Text)
    result: Mapped[str | None] = mapped_column(Text)    # JSON
    error: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[str | None] = mapped_column("metadata", Text)   # JSON
    created_at: Mapped[str] = mapped_column(default=lambda: utcnow().isoformat())
    updated_at: Mapped[str] = mapped_column(
        default=lambda: utcnow().isoformat(),
        onupdate=lambda: utcnow().isoformat(),
    )

    scenario = relationship("Scenario", back_populates="tasks")

    def set_result(self, data: dict) -> None:
        self.result = json.dumps(data)

    def get_result(self) -> dict:
        if not self.result:
            return {}
        return json.loads(self.result)
