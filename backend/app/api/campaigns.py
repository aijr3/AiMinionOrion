"""Campaign and KPI endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.models.strategy import Strategy
from app.models.campaign import Campaign, KPI, KpiSnapshot, CampaignStatus
from app.models.task import Task, TaskStatus

router = APIRouter(prefix="/api/v1", tags=["campaigns"])


class KpiSnapshotCreate(BaseModel):
    value: float
    note: Optional[str] = None


@router.post("/strategies/{strategy_id}/campaigns/plan")
async def plan_campaigns(
    strategy_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404)
    task = Task(scenario_id=strategy.scenario_id, task_type="campaign_planning")
    db.add(task)
    db.commit()
    db.refresh(task)

    async def _run(sid, tid):
        from app.models.base import SessionLocal
        from app.services.campaign_planner import CampaignPlanner
        _db = SessionLocal()
        try:
            _task = _db.query(Task).filter(Task.id == tid).first()
            _task.status = TaskStatus.processing
            _db.commit()
            await CampaignPlanner(_db).run(sid)
            _task.status = TaskStatus.completed
            _task.progress = 100
            _db.commit()
        except Exception as e:
            _task.status = TaskStatus.failed
            _task.error = str(e)
            _db.commit()
        finally:
            _db.close()

    background_tasks.add_task(_run, strategy.scenario_id, task.id)
    return {"success": True, "data": {"task_id": task.id}}


@router.get("/strategies/{strategy_id}/campaigns")
def list_campaigns(strategy_id: str, db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).filter(Campaign.strategy_id == strategy_id).all()
    return {"success": True, "data": [c.to_dict(include_kpis=True) for c in campaigns]}


@router.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    c = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not c:
        raise HTTPException(status_code=404)
    return {"success": True, "data": c.to_dict(include_kpis=True)}


@router.get("/campaigns/{campaign_id}/kpis/{kpi_id}/history")
def get_kpi_history(campaign_id: str, kpi_id: str, db: Session = Depends(get_db)):
    kpi = db.query(KPI).filter(KPI.id == kpi_id, KPI.campaign_id == campaign_id).first()
    if not kpi:
        raise HTTPException(status_code=404)
    snapshots = db.query(KpiSnapshot).filter(KpiSnapshot.kpi_id == kpi_id).order_by(
        KpiSnapshot.recorded_at.asc()
    ).all()
    return {"success": True, "data": {**kpi.to_dict(), "history": [s.to_dict() for s in snapshots]}}


@router.post("/campaigns/{campaign_id}/kpis/{kpi_id}/snapshot")
def record_kpi_snapshot(campaign_id: str, kpi_id: str, payload: KpiSnapshotCreate, db: Session = Depends(get_db)):
    kpi = db.query(KPI).filter(KPI.id == kpi_id, KPI.campaign_id == campaign_id).first()
    if not kpi:
        raise HTTPException(status_code=404)
    snap = KpiSnapshot(kpi_id=kpi_id, value=payload.value, note=payload.note)
    kpi.current_value = payload.value
    db.add(snap)
    db.commit()
    db.refresh(snap)
    return {"success": True, "data": snap.to_dict()}
