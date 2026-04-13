"""Persona ORM model — MBTI-typed psychographic profile."""
import json
from sqlalchemy import Text, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from .base import Base, new_uuid, utcnow


class PersonaType(str, enum.Enum):
    customer = "customer"
    opponent = "opponent"
    ally = "ally"
    neutral = "neutral"


class Persona(Base):
    __tablename__ = "personas"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    scenario_id: Mapped[str] = mapped_column(ForeignKey("scenarios.id", ondelete="CASCADE"))
    persona_type: Mapped[str] = mapped_column(SAEnum(PersonaType), default=PersonaType.customer)
    name: Mapped[str] = mapped_column(nullable=False)
    age_range: Mapped[str | None] = mapped_column()
    role: Mapped[str | None] = mapped_column()

    # MBTI
    mbti_type: Mapped[str | None] = mapped_column()          # e.g. "INTJ"
    mbti_reasoning: Mapped[str | None] = mapped_column(Text)
    decision_style: Mapped[str | None] = mapped_column(Text)
    stress_reaction: Mapped[str | None] = mapped_column(Text)
    motivational_levers: Mapped[str | None] = mapped_column(Text)  # JSON list

    # Behavioral
    goals: Mapped[str | None] = mapped_column(Text)              # JSON list
    pain_points: Mapped[str | None] = mapped_column(Text)        # JSON list
    motivations: Mapped[str | None] = mapped_column(Text)        # JSON list
    objections: Mapped[str | None] = mapped_column(Text)         # JSON list
    intent_signals: Mapped[str | None] = mapped_column(Text)     # JSON list of {signal, context, likelihood}
    platform_presence: Mapped[str | None] = mapped_column(Text)  # JSON {platform: bool}

    # Influence
    influence_score: Mapped[float | None] = mapped_column(Float)  # 0–1
    seduction_type: Mapped[str | None] = mapped_column()          # Greene Art of Seduction type
    bio: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[str] = mapped_column(default=lambda: utcnow().isoformat())

    scenario = relationship("Scenario", back_populates="personas")

    def _json(self, field) -> list:
        val = getattr(self, field)
        return json.loads(val) if val else []

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "scenario_id": self.scenario_id,
            "persona_type": self.persona_type,
            "name": self.name,
            "age_range": self.age_range,
            "role": self.role,
            "mbti_type": self.mbti_type,
            "mbti_reasoning": self.mbti_reasoning,
            "decision_style": self.decision_style,
            "stress_reaction": self.stress_reaction,
            "motivational_levers": self._json("motivational_levers"),
            "goals": self._json("goals"),
            "pain_points": self._json("pain_points"),
            "motivations": self._json("motivations"),
            "objections": self._json("objections"),
            "intent_signals": self._json("intent_signals"),
            "platform_presence": json.loads(self.platform_presence) if self.platform_presence else {},
            "influence_score": self.influence_score,
            "seduction_type": self.seduction_type,
            "bio": self.bio,
            "created_at": self.created_at,
        }
