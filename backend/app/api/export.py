"""Export endpoints — PDF and JSON downloads."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.models.scenario import Scenario
from app.services.export_service import ExportService

router = APIRouter(prefix="/api/v1", tags=["export"])


@router.post("/scenarios/{scenario_id}/export/json")
def export_json(scenario_id: str, db: Session = Depends(get_db)):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404)
    path = ExportService(db).export_json(scenario_id)
    return FileResponse(path=str(path), media_type="application/json", filename=path.name)


@router.post("/scenarios/{scenario_id}/export/pdf")
def export_pdf(scenario_id: str, db: Session = Depends(get_db)):
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404)
    path = ExportService(db).export_pdf(scenario_id)
    media_type = "application/pdf" if path.suffix == ".pdf" else "text/markdown"
    return FileResponse(path=str(path), media_type=media_type, filename=path.name)
