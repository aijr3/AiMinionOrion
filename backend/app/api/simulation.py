"""MiroFish simulation bridge endpoints."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.models.scenario import Scenario
from app.models.task import Task, TaskStatus
from app.services.simulation_bridge import SimulationBridge

router = APIRouter(prefix="/api/v1", tags=["simulation"])


@router.post("/scenarios/{scenario_id}/simulate")
async def launch_simulation(
    scenario_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404)
    task = Task(scenario_id=scenario_id, task_type="mirofish_simulation")
    db.add(task)
    db.commit()
    db.refresh(task)

    async def _run(sid, tid):
        from app.models.base import SessionLocal
        _db = SessionLocal()
        try:
            bridge = SimulationBridge(_db)
            result = await bridge.run_simulation(sid, tid)
            _task = _db.query(Task).filter(Task.id == tid).first()
            if result.get("status") in ("launched", "disabled", "unavailable"):
                _task.status = TaskStatus.completed
                _task.set_result(result)
            _db.commit()
        except Exception as e:
            _task = _db.query(Task).filter(Task.id == tid).first()
            if _task:
                _task.status = TaskStatus.failed
                _task.error = str(e)
                _db.commit()
        finally:
            _db.close()

    background_tasks.add_task(_run, scenario_id, task.id)
    return {"success": True, "data": {"task_id": task.id}}


@router.get("/scenarios/{scenario_id}/simulate/results")
async def get_simulation_results(scenario_id: str, db: Session = Depends(get_db)):
    bridge = SimulationBridge(db)
    result = await bridge.get_simulation_results(scenario_id)
    return {"success": True, "data": result}
