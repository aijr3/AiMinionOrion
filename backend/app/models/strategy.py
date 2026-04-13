"""Strategy and Tactic ORM models."""
import json
import enum
from sqlalchemy import Text, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, new_uuid, utcnow


class StrategyType(str, enum.Enum):
    win = "win"
    pivot = "pivot"
    graceful_exit = "graceful_exit"
    coexistence = "coexistence"


class StrategyApproach(str, enum.Enum):
    aggressive = "aggressive"
    defensive = "defensive"
    flanking = "flanking"
    guerrilla = "guerrilla"
    attrition = "attrition"
    sun_tzu = "sun_tzu"
    ooda = "ooda"
    partnership = "partnership"
    thought_leadership = "thought_leadership"
    seduction = "seduction"
    indirect = "indirect"


class Priority(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"


class Strategy(Base):
    __tablename__ = "strategies"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    scenario_id: Mapped[str] = mapped_column(ForeignKey("scenarios.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    strategic_objective: Mapped[str | None] = mapped_column(Text)
    strategy_type: Mapped[str] = mapped_column(SAEnum(StrategyType), default=StrategyType.win)
    approach: Mapped[str] = mapped_column(SAEnum(StrategyApproach), default=StrategyApproach.flanking)
    win_probability: Mapped[float | None] = mapped_column(Float)         # 0–1
    confidence_level: Mapped[float | None] = mapped_column(Float)        # 0–1
    confidence_interval_lower: Mapped[float | None] = mapped_column(Float)
    confidence_interval_upper: Mapped[float | None] = mapped_column(Float)
    frameworks_applied: Mapped[str | None] = mapped_column(Text)         # JSON list of strings
    supporting_evidence: Mapped[str | None] = mapped_column(Text)        # JSON list
    risks: Mapped[str | None] = mapped_column(Text)                      # JSON list of {risk, mitigation, probability}
    logic_explanation: Mapped[str | None] = mapped_column(Text)
    greene_laws_applied: Mapped[str | None] = mapped_column(Text)        # JSON list
    sun_tzu_principles: Mapped[str | None] = mapped_column(Text)         # JSON list
    created_at: Mapped[str] = mapped_column(default=lambda: utcnow().isoformat())

    scenario = relationship("Scenario", back_populates="strategies")
    tactics = relationship("Tactic", back_populates="strategy", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="strategy", cascade="all, delete-orphan")

    def to_dict(self, include_tactics: bool = False) -> dict:
        d = {
            "id": self.id,
            "scenario_id": self.scenario_id,
            "title": self.title,
            "summary": self.summary,
            "strategic_objective": self.strategic_objective,
            "strategy_type": self.strategy_type,
            "approach": self.approach,
            "win_probability": self.win_probability,
            "confidence_level": self.confidence_level,
            "confidence_interval": {
                "lower": self.confidence_interval_lower,
                "upper": self.confidence_interval_upper,
            },
            "frameworks_applied": json.loads(self.frameworks_applied) if self.frameworks_applied else [],
            "supporting_evidence": json.loads(self.supporting_evidence) if self.supporting_evidence else [],
            "risks": json.loads(self.risks) if self.risks else [],
            "logic_explanation": self.logic_explanation,
            "greene_laws_applied": json.loads(self.greene_laws_applied) if self.greene_laws_applied else [],
            "sun_tzu_principles": json.loads(self.sun_tzu_principles) if self.sun_tzu_principles else [],
            "created_at": self.created_at,
        }
        if include_tactics:
            d["tactics"] = [t.to_dict() for t in self.tactics]
        return d


class Tactic(Base):
    __tablename__ = "tactics"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    strategy_id: Mapped[str] = mapped_column(ForeignKey("strategies.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    framework_source: Mapped[str | None] = mapped_column()  # war/marketing/psychology/research/greene
    priority: Mapped[str] = mapped_column(SAEnum(Priority), default=Priority.medium)
    effort: Mapped[str] = mapped_column(SAEnum(Priority), default=Priority.medium)
    impact: Mapped[str] = mapped_column(SAEnum(Priority), default=Priority.medium)
    owner: Mapped[str | None] = mapped_column()
    due_date: Mapped[str | None] = mapped_column()
    success_metric: Mapped[str | None] = mapped_column(Text)
    greene_law_reference: Mapped[str | None] = mapped_column()
    created_at: Mapped[str] = mapped_column(default=lambda: utcnow().isoformat())

    strategy = relationship("Strategy", back_populates="tactics")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "strategy_id": self.strategy_id,
            "title": self.title,
            "description": self.description,
            "framework_source": self.framework_source,
            "priority": self.priority,
            "effort": self.effort,
            "impact": self.impact,
            "owner": self.owner,
            "due_date": self.due_date,
            "success_metric": self.success_metric,
            "greene_law_reference": self.greene_law_reference,
            "created_at": self.created_at,
        }
