"""Pain point endpoints."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.models.scenario import Scenario
from app.models.pain_point import PainPoint
from app.models.task import Task, TaskStatus

router = APIRouter(prefix="/api/v1", tags=["pain_points"])


@router.post("/scenarios/{scenario_id}/pain-points/extract")
async def extract_pain_points(
    scenario_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404)
    task = Task(scenario_id=scenario_id, task_type="pain_point_extraction")
    db.add(task)
    db.commit()
    db.refresh(task)

    async def _run(sid, tid):
        from app.models.base import SessionLocal
        from app.services.pain_point_extractor import PainPointExtractor
        _db = SessionLocal()
        try:
            _task = _db.query(Task).filter(Task.id == tid).first()
            _task.status = TaskStatus.processing
            _db.commit()
            await PainPointExtractor(_db).run(sid)
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


@router.get("/scenarios/{scenario_id}/pain-points")
def list_pain_points(scenario_id: str, db: Session = Depends(get_db)):
    pps = db.query(PainPoint).filter(PainPoint.scenario_id == scenario_id).all()
    return {"success": True, "data": [pp.to_dict() for pp in pps]}


@router.delete("/scenarios/{scenario_id}/pain-points/{pp_id}")
def delete_pain_point(scenario_id: str, pp_id: str, db: Session = Depends(get_db)):
    pp = db.query(PainPoint).filter(PainPoint.id == pp_id, PainPoint.scenario_id == scenario_id).first()
    if not pp:
        raise HTTPException(status_code=404)
    db.delete(pp)
    db.commit()
    return {"success": True, "data": {"deleted": pp_id}}
