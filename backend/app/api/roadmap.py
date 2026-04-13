"""Roadmap endpoints."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.models.scenario import Scenario
from app.models.roadmap import RoadmapStep
from app.models.task import Task, TaskStatus

router = APIRouter(prefix="/api/v1", tags=["roadmap"])


@router.post("/scenarios/{scenario_id}/roadmap/build")
async def build_roadmap(
    scenario_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404)
    task = Task(scenario_id=scenario_id, task_type="roadmap_building")
    db.add(task)
    db.commit()
    db.refresh(task)

    async def _run(sid, tid):
        from app.models.base import SessionLocal
        from app.services.roadmap_builder import RoadmapBuilder
        _db = SessionLocal()
        try:
            _task = _db.query(Task).filter(Task.id == tid).first()
            _task.status = TaskStatus.processing
            _db.commit()
            await RoadmapBuilder(_db).run(sid)
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


@router.get("/scenarios/{scenario_id}/roadmap")
def get_roadmap(scenario_id: str, db: Session = Depends(get_db)):
    steps = db.query(RoadmapStep).filter(RoadmapStep.scenario_id == scenario_id).order_by(
        RoadmapStep.path_type, RoadmapStep.step_number
    ).all()
    win_steps = [s for s in steps if s.path_type == "win"]
    gf_steps = [s for s in steps if s.path_type == "graceful_forward"]
    final_win_prob = win_steps[-1].cumulative_probability if win_steps else None
    return {
        "success": True,
        "data": {
            "win_path": [s.to_dict() for s in win_steps],
            "graceful_forward_path": [s.to_dict() for s in gf_steps],
            "win_path_final_probability": final_win_prob,
        },
    }


@router.get("/scenarios/{scenario_id}/roadmap/probability")
def get_win_probability(scenario_id: str, db: Session = Depends(get_db)):
    last_step = db.query(RoadmapStep).filter(
        RoadmapStep.scenario_id == scenario_id,
        RoadmapStep.path_type == "win",
    ).order_by(RoadmapStep.step_number.desc()).first()
    return {
        "success": True,
        "data": {
            "cumulative_win_probability": last_step.cumulative_probability if last_step else None,
        },
    }


class StepUpdate(BaseModel):
    is_complete: bool | None = None
    title: str | None = None


@router.put("/scenarios/{scenario_id}/roadmap/steps/{step_id}")
def update_step(scenario_id: str, step_id: str, payload: StepUpdate, db: Session = Depends(get_db)):
    step = db.query(RoadmapStep).filter(RoadmapStep.id == step_id, RoadmapStep.scenario_id == scenario_id).first()
    if not step:
        raise HTTPException(status_code=404)
    if payload.is_complete is not None:
        step.is_complete = payload.is_complete
    if payload.title is not None:
        step.title = payload.title
    db.commit()
    return {"success": True, "data": step.to_dict()}
