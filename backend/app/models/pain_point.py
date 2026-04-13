"""PainPoint ORM model."""
import json
import enum
from sqlalchemy import Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, new_uuid, utcnow


class Severity(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class PainCategory(str, enum.Enum):
    product = "product"
    process = "process"
    people = "people"
    technology = "technology"
    market = "market"
    psychological = "psychological"
    power = "power"


class PainPoint(Base):
    __tablename__ = "pain_points"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    scenario_id: Mapped[str] = mapped_column(ForeignKey("scenarios.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(SAEnum(Severity), default=Severity.medium)
    category: Mapped[str] = mapped_column(SAEnum(PainCategory), default=PainCategory.process)
    affected_persona_ids: Mapped[str | None] = mapped_column(Text)  # JSON list of persona UUIDs
    root_cause: Mapped[str | None] = mapped_column(Text)
    proposed_solution: Mapped[str | None] = mapped_column(Text)
    effort_to_fix: Mapped[str | None] = mapped_column()
    if_unresolved_impact: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(default=lambda: utcnow().isoformat())

    scenario = relationship("Scenario", back_populates="pain_points")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "scenario_id": self.scenario_id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "category": self.category,
            "affected_persona_ids": json.loads(self.affected_persona_ids) if self.affected_persona_ids else [],
            "root_cause": self.root_cause,
            "proposed_solution": self.proposed_solution,
            "effort_to_fix": self.effort_to_fix,
            "if_unresolved_impact": self.if_unresolved_impact,
            "created_at": self.created_at,
        }
