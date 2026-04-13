"""Competitive analysis endpoints."""
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.models.scenario import Scenario
from app.models.competitor import Competitor
from app.models.framework_analysis import FrameworkAnalysis
from app.models.task import Task, TaskStatus

router = APIRouter(prefix="/api/v1", tags=["analysis"])


class CompetitorCreate(BaseModel):
    name: str
    description: Optional[str] = None
    market_share: Optional[float] = None
    positioning: Optional[str] = None
    website: Optional[str] = None
    threat_level: Optional[str] = None


@router.post("/scenarios/{scenario_id}/analysis/run")
async def run_analysis(
    scenario_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404)
    task = Task(scenario_id=scenario_id, task_type="competitive_analysis")
    db.add(task)
    db.commit()
    db.refresh(task)

    async def _run(sid, tid):
        from app.models.base import SessionLocal
        from app.services.analysis_engine import AnalysisEngine
        _db = SessionLocal()
        try:
            _task = _db.query(Task).filter(Task.id == tid).first()
            _task.status = TaskStatus.processing
            _db.commit()
            await AnalysisEngine(_db).run(sid)
            _task.status = TaskStatus.completed
            _task.progress = 100
            _db.commit()
        except Exception as e:
            _task.status = TaskStatus.failed
            _task.error = str(e)
            _db.commit()
        finally:
            _db.close()

    background_tasks.add_task(_run, scenario_id, task.id)
    return {"success": True, "data": {"task_id": task.id}}


@router.get("/scenarios/{scenario_id}/analysis")
def get_analysis(scenario_id: str, db: Session = Depends(get_db)):
    competitors = db.query(Competitor).filter(Competitor.scenario_id == scenario_id).all()
    frameworks = db.query(FrameworkAnalysis).filter(
        FrameworkAnalysis.scenario_id == scenario_id,
        FrameworkAnalysis.framework_type == "research",
    ).all()
    return {
        "success": True,
        "data": {
            "competitors": [c.to_dict() for c in competitors],
            "framework_summaries": [f.to_dict() for f in frameworks],
        },
    }


@router.post("/scenarios/{scenario_id}/competitors")
def add_competitor(scenario_id: str, payload: CompetitorCreate, db: Session = Depends(get_db)):
    comp = Competitor(
        scenario_id=scenario_id,
        name=payload.name,
        description=payload.description,
        market_share=payload.market_share,
        positioning=payload.positioning,
        website=payload.website,
        threat_level=payload.threat_level,
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return {"success": True, "data": comp.to_dict()}


@router.put("/scenarios/{scenario_id}/competitors/{competitor_id}")
def update_competitor(
    scenario_id: str, competitor_id: str, payload: CompetitorCreate, db: Session = Depends(get_db)
):
    comp = db.query(Competitor).filter(
        Competitor.id == competitor_id, Competitor.scenario_id == scenario_id
    ).first()
    if not comp:
        raise HTTPException(status_code=404)
    for field, val in payload.dict(exclude_none=True).items():
        setattr(comp, field, val)
    db.commit()
    db.refresh(comp)
    return {"success": True, "data": comp.to_dict()}


@router.delete("/scenarios/{scenario_id}/competitors/{competitor_id}")
def delete_competitor(scenario_id: str, competitor_id: str, db: Session = Depends(get_db)):
    comp = db.query(Competitor).filter(
        Competitor.id == competitor_id, Competitor.scenario_id == scenario_id
    ).first()
    if not comp:
        raise HTTPException(status_code=404)
    db.delete(comp)
    db.commit()
    return {"success": True, "data": {"deleted": competitor_id}}
