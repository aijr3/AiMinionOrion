"""Campaign, KPI, and KpiSnapshot ORM models."""
import json
import enum
from sqlalchemy import Text, Float, Integer, ForeignKey, Enum as SAEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, new_uuid, utcnow


class AidaPhase(str, enum.Enum):
    awareness = "awareness"
    interest = "interest"
    desire = "desire"
    action = "action"
    retention = "retention"


class CampaignStatus(str, enum.Enum):
    planned = "planned"
    active = "active"
    paused = "paused"
    completed = "completed"


class MeasurementFrequency(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    strategy_id: Mapped[str] = mapped_column(ForeignKey("strategies.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(nullable=False)
    objective: Mapped[str | None] = mapped_column(Text)
    aida_phase: Mapped[str] = mapped_column(SAEnum(AidaPhase), default=AidaPhase.awareness)
    campaign_type: Mapped[str | None] = mapped_column()
    channels: Mapped[str | None] = mapped_column(Text)          # JSON list of strings
    google_ads_compatible: Mapped[bool] = mapped_column(Boolean, default=False)
    key_messages: Mapped[str | None] = mapped_column(Text)      # JSON list
    owner: Mapped[str | None] = mapped_column()
    start_date: Mapped[str | None] = mapped_column()
    end_date: Mapped[str | None] = mapped_column()
    budget: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = mapped_column(SAEnum(CampaignStatus), default=CampaignStatus.planned)
    success_definition: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(default=lambda: utcnow().isoformat())

    strategy = relationship("Strategy", back_populates="campaigns")
    kpis = relationship("KPI", back_populates="campaign", cascade="all, delete-orphan")

    def to_dict(self, include_kpis: bool = False) -> dict:
        d = {
            "id": self.id,
            "strategy_id": self.strategy_id,
            "name": self.name,
            "objective": self.objective,
            "aida_phase": self.aida_phase,
            "campaign_type": self.campaign_type,
            "channels": json.loads(self.channels) if self.channels else [],
            "google_ads_compatible": self.google_ads_compatible,
            "key_messages": json.loads(self.key_messages) if self.key_messages else [],
            "owner": self.owner,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "budget": self.budget,
            "status": self.status,
            "success_definition": self.success_definition,
            "created_at": self.created_at,
        }
        if include_kpis:
            d["kpis"] = [k.to_dict() for k in self.kpis]
        return d


class KPI(Base):
    __tablename__ = "kpis"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    target_value: Mapped[float | None] = mapped_column(Float)
    current_value: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[str | None] = mapped_column()
    measurement_frequency: Mapped[str] = mapped_column(
        SAEnum(MeasurementFrequency), default=MeasurementFrequency.weekly
    )
    created_at: Mapped[str] = mapped_column(default=lambda: utcnow().isoformat())
    updated_at: Mapped[str] = mapped_column(
        default=lambda: utcnow().isoformat(),
        onupdate=lambda: utcnow().isoformat(),
    )

    campaign = relationship("Campaign", back_populates="kpis")
    snapshots = relationship("KpiSnapshot", back_populates="kpi", cascade="all, delete-orphan")

    @property
    def progress_pct(self) -> float | None:
        if self.target_value and self.target_value > 0:
            return min(100.0, (self.current_value / self.target_value) * 100)
        return None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "name": self.name,
            "description": self.description,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "unit": self.unit,
            "measurement_frequency": self.measurement_frequency,
            "progress_pct": self.progress_pct,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class KpiSnapshot(Base):
    __tablename__ = "kpi_snapshots"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    kpi_id: Mapped[str] = mapped_column(ForeignKey("kpis.id", ondelete="CASCADE"))
    recorded_at: Mapped[str] = mapped_column(default=lambda: utcnow().isoformat())
    value: Mapped[float] = mapped_column(Float)
    note: Mapped[str | None] = mapped_column(Text)

    kpi = relationship("KPI", back_populates="snapshots")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "kpi_id": self.kpi_id,
            "recorded_at": self.recorded_at,
            "value": self.value,
            "note": self.note,
        }
