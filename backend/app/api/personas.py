"""Persona endpoints."""
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.models.scenario import Scenario
from app.models.persona import Persona
from app.models.task import Task, TaskStatus

router = APIRouter(prefix="/api/v1", tags=["personas"])


class PersonaCreate(BaseModel):
    name: str
    persona_type: str = "customer"
    age_range: Optional[str] = None
    role: Optional[str] = None
    mbti_type: Optional[str] = None
    bio: Optional[str] = None
    influence_score: Optional[float] = None


@router.post("/scenarios/{scenario_id}/personas/build")
async def build_personas(
    scenario_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404)
    task = Task(scenario_id=scenario_id, task_type="persona_building")
    db.add(task)
    db.commit()
    db.refresh(task)

    async def _run(sid, tid):
        from app.models.base import SessionLocal
        from app.services.persona_builder import PersonaBuilder
        _db = SessionLocal()
        try:
            _task = _db.query(Task).filter(Task.id == tid).first()
            _task.status = TaskStatus.processing
            _db.commit()
            await PersonaBuilder(_db).run(sid)
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


@router.get("/scenarios/{scenario_id}/personas")
def list_personas(scenario_id: str, db: Session = Depends(get_db)):
    personas = db.query(Persona).filter(Persona.scenario_id == scenario_id).all()
    return {"success": True, "data": [p.to_dict() for p in personas]}


@router.get("/scenarios/{scenario_id}/personas/{persona_id}")
def get_persona(scenario_id: str, persona_id: str, db: Session = Depends(get_db)):
    p = db.query(Persona).filter(Persona.id == persona_id, Persona.scenario_id == scenario_id).first()
    if not p:
        raise HTTPException(status_code=404)
    return {"success": True, "data": p.to_dict()}


@router.post("/scenarios/{scenario_id}/personas")
def create_persona(scenario_id: str, payload: PersonaCreate, db: Session = Depends(get_db)):
    p = Persona(scenario_id=scenario_id, **payload.dict())
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"success": True, "data": p.to_dict()}


@router.delete("/scenarios/{scenario_id}/personas/{persona_id}")
def delete_persona(scenario_id: str, persona_id: str, db: Session = Depends(get_db)):
    p = db.query(Persona).filter(Persona.id == persona_id, Persona.scenario_id == scenario_id).first()
    if not p:
        raise HTTPException(status_code=404)
    db.delete(p)
    db.commit()
    return {"success": True, "data": {"deleted": persona_id}}
