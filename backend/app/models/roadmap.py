"""RoadmapStep ORM model."""
import json
import enum
from sqlalchemy import Text, Float, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, new_uuid, utcnow


class PathType(str, enum.Enum):
    win = "win"
    graceful_forward = "graceful_forward"


class RoadmapStep(Base):
    __tablename__ = "roadmap_steps"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    scenario_id: Mapped[str] = mapped_column(ForeignKey("scenarios.id", ondelete="CASCADE"))
    step_number: Mapped[int] = mapped_column(Integer)
    path_type: Mapped[str] = mapped_column(SAEnum(PathType), default=PathType.win)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    milestone: Mapped[str | None] = mapped_column(Text)
    probability_of_success: Mapped[float | None] = mapped_column(Float)   # 0–1
    cumulative_probability: Mapped[float | None] = mapped_column(Float)   # running product
    probability_rationale: Mapped[str | None] = mapped_column(Text)
    dependencies: Mapped[str | None] = mapped_column(Text)               # JSON list of step numbers
    owner: Mapped[str | None] = mapped_column()
    estimated_duration: Mapped[str | None] = mapped_column()
    risk_factors: Mapped[str | None] = mapped_column(Text)               # JSON list
    is_complete: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[str] = mapped_column(default=lambda: utcnow().isoformat())

    scenario = relationship("Scenario", back_populates="roadmap_steps")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "scenario_id": self.scenario_id,
            "step_number": self.step_number,
            "path_type": self.path_type,
            "title": self.title,
            "description": self.description,
            "milestone": self.milestone,
            "probability_of_success": self.probability_of_success,
            "cumulative_probability": self.cumulative_probability,
            "probability_rationale": self.probability_rationale,
            "dependencies": json.loads(self.dependencies) if self.dependencies else [],
            "owner": self.owner,
            "estimated_duration": self.estimated_duration,
            "risk_factors": json.loads(self.risk_factors) if self.risk_factors else [],
            "is_complete": self.is_complete,
            "created_at": self.created_at,
        }
