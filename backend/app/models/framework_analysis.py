"""FrameworkAnalysis ORM model — stores results from each analytical framework."""
import json
import enum
from sqlalchemy import Text, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, new_uuid, utcnow


class FrameworkType(str, enum.Enum):
    war = "war"
    marketing = "marketing"
    psychology = "psychology"
    research = "research"
    robert_greene = "robert_greene"
    mbti = "mbti"
    probability = "probability"


class FrameworkAnalysis(Base):
    __tablename__ = "framework_analyses"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    scenario_id: Mapped[str] = mapped_column(ForeignKey("scenarios.id", ondelete="CASCADE"))
    framework_name: Mapped[str] = mapped_column(nullable=False)
    framework_type: Mapped[str] = mapped_column(SAEnum(FrameworkType))
    summary: Mapped[str | None] = mapped_column(Text)
    key_insights: Mapped[str | None] = mapped_column(Text)    # JSON list
    raw_output: Mapped[str | None] = mapped_column(Text)      # Full LLM JSON output
    applicability_score: Mapped[float | None] = mapped_column(Float)  # 0–1
    created_at: Mapped[str] = mapped_column(default=lambda: utcnow().isoformat())

    scenario = relationship("Scenario", back_populates="framework_analyses")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "scenario_id": self.scenario_id,
            "framework_name": self.framework_name,
            "framework_type": self.framework_type,
            "summary": self.summary,
            "key_insights": json.loads(self.key_insights) if self.key_insights else [],
            "raw_output": json.loads(self.raw_output) if self.raw_output else {},
            "applicability_score": self.applicability_score,
            "created_at": self.created_at,
        }
