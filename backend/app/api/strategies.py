"""Strategy and tactic endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.models.scenario import Scenario
from app.models.strategy import Strategy, Tactic
from app.models.task import Task, TaskStatus
from app.utils.prompt_loader import load_prompt
from app.utils.llm_client import LLMClient

router = APIRouter(prefix="/api/v1", tags=["strategies"])


class TacticCreate(BaseModel):
    title: str
    description: Optional[str] = None
    framework_source: Optional[str] = None
    priority: str = "medium"
    effort: str = "medium"
    impact: str = "medium"
    success_metric: Optional[str] = None
    greene_law_reference: Optional[str] = None


@router.post("/scenarios/{scenario_id}/strategies/generate")
async def generate_strategies(
    scenario_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404)
    task = Task(scenario_id=scenario_id, task_type="strategy_generation")
    db.add(task)
    db.commit()
    db.refresh(task)

    async def _run(sid, tid):
        from app.models.base import SessionLocal
        from app.services.strategy_generator import StrategyGenerator
        from app.services.probability_engine import ProbabilityEngine
        _db = SessionLocal()
        try:
            _task = _db.query(Task).filter(Task.id == tid).first()
            _task.status = TaskStatus.processing
            _db.commit()
            await StrategyGenerator(_db).run(sid)
            await ProbabilityEngine(_db).run(sid)
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


@router.get("/scenarios/{scenario_id}/strategies")
def list_strategies(scenario_id: str, db: Session = Depends(get_db)):
    strategies = db.query(Strategy).filter(Strategy.scenario_id == scenario_id).all()
    return {"success": True, "data": [s.to_dict(include_tactics=True) for s in strategies]}


@router.get("/scenarios/{scenario_id}/strategies/{strategy_id}")
def get_strategy(scenario_id: str, strategy_id: str, db: Session = Depends(get_db)):
    s = db.query(Strategy).filter(Strategy.id == strategy_id, Strategy.scenario_id == scenario_id).first()
    if not s:
        raise HTTPException(status_code=404)
    return {"success": True, "data": s.to_dict(include_tactics=True)}


@router.get("/scenarios/{scenario_id}/strategies/{strategy_id}/explanation")
async def get_explanation(scenario_id: str, strategy_id: str, db: Session = Depends(get_db)):
    """Returns the full logic explanation, generating it if not yet present."""
    s = db.query(Strategy).filter(Strategy.id == strategy_id, Strategy.scenario_id == scenario_id).first()
    if not s:
        raise HTTPException(status_code=404)

    if not s.logic_explanation:
        from app.models.scenario import Scenario as ScenarioModel
        scenario = db.query(ScenarioModel).filter(ScenarioModel.id == scenario_id).first()
        llm = LLMClient()
        explanation = await llm.chat(
            system="You are a strategy communicator. Write a clear structured explanation.",
            user=load_prompt(
                "logic_explanation",
                recommendation_title=s.title,
                recommendation_details=s.summary or "",
                scenario_context=scenario.market_context or scenario.description or "",
                framework_context="",
                competitive_context="",
            ),
        )
        s.logic_explanation = explanation
        db.commit()

    return {"success": True, "data": {"logic_explanation": s.logic_explanation}}


@router.delete("/scenarios/{scenario_id}/strategies/{strategy_id}")
def delete_strategy(scenario_id: str, strategy_id: str, db: Session = Depends(get_db)):
    s = db.query(Strategy).filter(Strategy.id == strategy_id, Strategy.scenario_id == scenario_id).first()
    if not s:
        raise HTTPException(status_code=404)
    db.delete(s)
    db.commit()
    return {"success": True, "data": {"deleted": strategy_id}}


@router.post("/scenarios/{scenario_id}/strategies/{strategy_id}/tactics")
def add_tactic(scenario_id: str, strategy_id: str, payload: TacticCreate, db: Session = Depends(get_db)):
    s = db.query(Strategy).filter(Strategy.id == strategy_id, Strategy.scenario_id == scenario_id).first()
    if not s:
        raise HTTPException(status_code=404)
    t = Tactic(strategy_id=strategy_id, **payload.dict())
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"success": True, "data": t.to_dict()}


@router.delete("/scenarios/{scenario_id}/strategies/{strategy_id}/tactics/{tactic_id}")
def delete_tactic(scenario_id: str, strategy_id: str, tactic_id: str, db: Session = Depends(get_db)):
    t = db.query(Tactic).filter(Tactic.id == tactic_id, Tactic.strategy_id == strategy_id).first()
    if not t:
        raise HTTPException(status_code=404)
    db.delete(t)
    db.commit()
    return {"success": True, "data": {"deleted": tactic_id}}
