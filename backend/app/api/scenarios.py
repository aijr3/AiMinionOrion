"""Scenario CRUD and pipeline trigger endpoints."""
import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.models.scenario import Scenario, ScenarioStatus, ScenarioType
from app.models.task import Task, TaskStatus
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["scenarios"])


class ScenarioCreate(BaseModel):
    name: str
    description: Optional[str] = None
    market_context: Optional[str] = None
    goals: Optional[list[str]] = None
    scenario_type: str = "business"
    industry: Optional[str] = None
    geography: Optional[str] = None
    time_horizon: Optional[str] = None


class ScenarioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    market_context: Optional[str] = None
    goals: Optional[list[str]] = None
    industry: Optional[str] = None
    geography: Optional[str] = None
    time_horizon: Optional[str] = None


def _scenario_dict(s: Scenario) -> dict:
    return {
        "id": s.id,
        "name": s.name,
        "description": s.description,
        "market_context": s.market_context,
        "goals": s.goals_list(),
        "scenario_type": s.scenario_type,
        "industry": s.industry,
        "geography": s.geography,
        "time_horizon": s.time_horizon,
        "status": s.status,
        "mirofish_project_id": s.mirofish_project_id,
        "created_at": s.created_at,
        "updated_at": s.updated_at,
    }


@router.post("/scenarios")
async def create_scenario(payload: ScenarioCreate, db: Session = Depends(get_db)):
    scenario = Scenario(
        name=payload.name,
        description=payload.description,
        market_context=payload.market_context,
        goals=json.dumps(payload.goals or []),
        scenario_type=payload.scenario_type,
        industry=payload.industry,
        geography=payload.geography,
        time_horizon=payload.time_horizon,
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    logger.info("Created scenario %s", scenario.id)
    return {"success": True, "data": _scenario_dict(scenario)}


@router.get("/scenarios")
def list_scenarios(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    scenarios = db.query(Scenario).order_by(Scenario.created_at.desc()).offset(skip).limit(limit).all()
    return {"success": True, "data": [_scenario_dict(s) for s in scenarios]}


@router.get("/scenarios/{scenario_id}")
def get_scenario(scenario_id: str, db: Session = Depends(get_db)):
    s = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return {"success": True, "data": _scenario_dict(s)}


@router.put("/scenarios/{scenario_id}")
def update_scenario(scenario_id: str, payload: ScenarioUpdate, db: Session = Depends(get_db)):
    s = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Scenario not found")
    if payload.name is not None:
        s.name = payload.name
    if payload.description is not None:
        s.description = payload.description
    if payload.market_context is not None:
        s.market_context = payload.market_context
    if payload.goals is not None:
        s.goals = json.dumps(payload.goals)
    if payload.industry is not None:
        s.industry = payload.industry
    if payload.geography is not None:
        s.geography = payload.geography
    if payload.time_horizon is not None:
        s.time_horizon = payload.time_horizon
    db.commit()
    db.refresh(s)
    return {"success": True, "data": _scenario_dict(s)}


@router.delete("/scenarios/{scenario_id}")
def delete_scenario(scenario_id: str, db: Session = Depends(get_db)):
    s = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Scenario not found")
    db.delete(s)
    db.commit()
    return {"success": True, "data": {"deleted": scenario_id}}


@router.post("/scenarios/{scenario_id}/run-analysis")
async def run_full_analysis(
    scenario_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Triggers the full async analysis pipeline for a scenario."""
    s = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Scenario not found")

    task = Task(scenario_id=scenario_id, task_type="full_analysis", status=TaskStatus.pending)
    db.add(task)
    s.status = ScenarioStatus.analyzing
    db.commit()
    db.refresh(task)

    background_tasks.add_task(_run_pipeline, scenario_id, task.id)
    return {"success": True, "data": {"task_id": task.id, "scenario_id": scenario_id}}


async def _run_pipeline(scenario_id: str, task_id: str):
    """Background pipeline: runs all analysis services sequentially."""
    from app.models.base import SessionLocal
    from app.services.analysis_engine import AnalysisEngine
    from app.services.mbti_profiler import MBTIProfiler
    from app.services.war_strategy_overlay import WarStrategyOverlay
    from app.services.robert_greene_analyzer import RobertGreeneAnalyzer
    from app.services.persona_builder import PersonaBuilder
    from app.services.strategy_generator import StrategyGenerator
    from app.services.probability_engine import ProbabilityEngine
    from app.services.pain_point_extractor import PainPointExtractor
    from app.services.campaign_planner import CampaignPlanner
    from app.services.roadmap_builder import RoadmapBuilder

    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        task.status = TaskStatus.processing
        task.progress = 5
        task.message = "Starting analysis pipeline..."
        db.commit()

        steps = [
            (AnalysisEngine, "Analyzing competitive landscape...", 15),
            (MBTIProfiler, "Profiling MBTI types for key players...", 25),
            (WarStrategyOverlay, "Applying war strategy frameworks...", 35),
            (RobertGreeneAnalyzer, "Applying Robert Greene frameworks...", 45),
            (PersonaBuilder, "Building detailed personas...", 55),
            (StrategyGenerator, "Generating strategic options...", 70),
            (PainPointExtractor, "Extracting pain points...", 80),
            (CampaignPlanner, "Planning campaigns...", 88),
            (RoadmapBuilder, "Building victory roadmap...", 96),
        ]

        for ServiceClass, msg, progress in steps:
            task.message = msg
            task.progress = progress
            db.commit()
            try:
                await ServiceClass(db).run(scenario_id)
            except Exception as e:
                logger.error("Pipeline step %s failed: %s", ServiceClass.__name__, e)
                # Non-fatal: continue pipeline

        scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if scenario:
            scenario.status = ScenarioStatus.ready
        task.status = TaskStatus.completed
        task.progress = 100
        task.message = "Analysis complete."
        db.commit()
        logger.info("Pipeline complete for scenario %s", scenario_id)
    except Exception as e:
        logger.error("Pipeline failed for scenario %s: %s", scenario_id, e)
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = TaskStatus.failed
            task.error = str(e)
            db.commit()
    finally:
        db.close()
