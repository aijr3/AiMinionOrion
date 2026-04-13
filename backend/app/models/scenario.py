"""Scenario ORM model — the root entity for every strategic analysis."""
import enum
import json

from sqlalchemy import Text, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, new_uuid, utcnow


class ScenarioStatus(str, enum.Enum):
    created = "created"
    analyzing = "analyzing"
    analyzed = "analyzed"
    strategizing = "strategizing"
    ready = "ready"
    archived = "archived"


class ScenarioType(str, enum.Enum):
    business = "business"
    political = "political"
    personal = "personal"
    negotiation = "negotiation"
    product_launch = "product_launch"
    market_entry = "market_entry"
    other = "other"


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    market_context: Mapped[str | None] = mapped_column(Text)
    goals: Mapped[str | None] = mapped_column(Text)          # JSON list of strings
    scenario_type: Mapped[str] = mapped_column(
        SAEnum(ScenarioType), default=ScenarioType.business
    )
    industry: Mapped[str | None] = mapped_column()
    geography: Mapped[str | None] = mapped_column()
    time_horizon: Mapped[str | None] = mapped_column()
    status: Mapped[str] = mapped_column(
        SAEnum(ScenarioStatus), default=ScenarioStatus.created
    )
    mirofish_project_id: Mapped[str | None] = mapped_column()
    mirofish_graph_id: Mapped[str | None] = mapped_column()
    mirofish_report: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(default=lambda: utcnow().isoformat())
    updated_at: Mapped[str] = mapped_column(
        default=lambda: utcnow().isoformat(),
        onupdate=lambda: utcnow().isoformat(),
    )

    # Relationships
    competitors = relationship("Competitor", back_populates="scenario", cascade="all, delete-orphan")
    personas = relationship("Persona", back_populates="scenario", cascade="all, delete-orphan")
    strategies = relationship("Strategy", back_populates="scenario", cascade="all, delete-orphan")
    pain_points = relationship("PainPoint", back_populates="scenario", cascade="all, delete-orphan")
    roadmap_steps = relationship("RoadmapStep", back_populates="scenario", cascade="all, delete-orphan")
    framework_analyses = relationship("FrameworkAnalysis", back_populates="scenario", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="scenario", cascade="all, delete-orphan")

    def goals_list(self) -> list[str]:
        if not self.goals:
            return []
        try:
            return json.loads(self.goals)
        except Exception:
            return [self.goals]
