"""Task status endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.models.task import Task

router = APIRouter(prefix="/api/v1", tags=["tasks"])


@router.get("/tasks/{task_id}")
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "success": True,
        "data": {
            "id": task.id,
            "task_type": task.task_type,
            "status": task.status,
            "progress": task.progress,
            "message": task.message,
            "result": task.get_result(),
            "error": task.error,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
        },
    }
