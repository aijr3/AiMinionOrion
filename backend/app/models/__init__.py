# Import all models so SQLAlchemy registers them with Base.metadata
from .base import Base, engine, SessionLocal, get_db, new_uuid, utcnow
from .scenario import Scenario, ScenarioStatus, ScenarioType
from .task import Task, TaskStatus
from .competitor import Competitor
from .persona import Persona, PersonaType
from .strategy import Strategy, Tactic, StrategyType, StrategyApproach, Priority
from .pain_point import PainPoint, Severity, PainCategory
from .campaign import Campaign, KPI, KpiSnapshot, AidaPhase, CampaignStatus
from .roadmap import RoadmapStep, PathType
from .framework_analysis import FrameworkAnalysis, FrameworkType

__all__ = [
    "Base", "engine", "SessionLocal", "get_db", "new_uuid", "utcnow",
    "Scenario", "ScenarioStatus", "ScenarioType",
    "Task", "TaskStatus",
    "Competitor",
    "Persona", "PersonaType",
    "Strategy", "Tactic", "StrategyType", "StrategyApproach", "Priority",
    "PainPoint", "Severity", "PainCategory",
    "Campaign", "KPI", "KpiSnapshot", "AidaPhase", "CampaignStatus",
    "RoadmapStep", "PathType",
    "FrameworkAnalysis", "FrameworkType",
]
