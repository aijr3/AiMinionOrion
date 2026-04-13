"""Metrics dashboard endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.models.scenario import Scenario
from app.services.metrics_aggregator import MetricsAggregator

router = APIRouter(prefix="/api/v1", tags=["metrics"])


@router.get("/scenarios/{scenario_id}/metrics")
def get_dashboard(scenario_id: str, db: Session = Depends(get_db)):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404)
    data = MetricsAggregator(db).get_dashboard(scenario_id)
    return {"success": True, "data": data}
