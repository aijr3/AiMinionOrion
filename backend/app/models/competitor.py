"""Competitor ORM model."""
import json
from sqlalchemy import Text, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, new_uuid, utcnow


class Competitor(Base):
    __tablename__ = "competitors"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    scenario_id: Mapped[str] = mapped_column(ForeignKey("scenarios.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    market_share: Mapped[float | None] = mapped_column(Float)       # 0–1
    strengths: Mapped[str | None] = mapped_column(Text)              # JSON list
    weaknesses: Mapped[str | None] = mapped_column(Text)             # JSON list
    positioning: Mapped[str | None] = mapped_column(Text)
    website: Mapped[str | None] = mapped_column()
    threat_level: Mapped[str | None] = mapped_column()              # critical/high/medium/low
    sentiment_score: Mapped[float | None] = mapped_column(Float)    # -1 to 1
    mbti_type: Mapped[str | None] = mapped_column()
    center_of_gravity: Mapped[str | None] = mapped_column(Text)     # Clausewitz CoG
    likely_response: Mapped[str | None] = mapped_column(Text)
    evidence_citations: Mapped[str | None] = mapped_column(Text)    # JSON list
    created_at: Mapped[str] = mapped_column(default=lambda: utcnow().isoformat())

    scenario = relationship("Scenario", back_populates="competitors")

    def strengths_list(self) -> list[str]:
        return json.loads(self.strengths) if self.strengths else []

    def weaknesses_list(self) -> list[str]:
        return json.loads(self.weaknesses) if self.weaknesses else []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "scenario_id": self.scenario_id,
            "name": self.name,
            "description": self.description,
            "market_share": self.market_share,
            "strengths": self.strengths_list(),
            "weaknesses": self.weaknesses_list(),
            "positioning": self.positioning,
            "website": self.website,
            "threat_level": self.threat_level,
            "sentiment_score": self.sentiment_score,
            "mbti_type": self.mbti_type,
            "center_of_gravity": self.center_of_gravity,
            "likely_response": self.likely_response,
            "evidence_citations": json.loads(self.evidence_citations) if self.evidence_citations else [],
            "created_at": self.created_at,
        }
