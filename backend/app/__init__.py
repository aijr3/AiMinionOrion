"""FastAPI application factory."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.base import Base, engine


def create_app() -> FastAPI:
    app = FastAPI(
        title="Miro Strategy App API",
        description="Universal strategic advisor — competitive analysis, personas, campaigns, and roadmaps",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Register routers
    from app.api.scenarios import router as scenarios_router
    from app.api.analysis import router as analysis_router
    from app.api.personas import router as personas_router
    from app.api.strategies import router as strategies_router
    from app.api.pain_points import router as pain_points_router
    from app.api.campaigns import router as campaigns_router
    from app.api.roadmap import router as roadmap_router
    from app.api.metrics import router as metrics_router
    from app.api.simulation import router as simulation_router
    from app.api.export import router as export_router
    from app.api.tasks import router as tasks_router
    from app.api.settings import router as settings_router

    app.include_router(scenarios_router)
    app.include_router(analysis_router)
    app.include_router(personas_router)
    app.include_router(strategies_router)
    app.include_router(pain_points_router)
    app.include_router(campaigns_router)
    app.include_router(roadmap_router)
    app.include_router(metrics_router)
    app.include_router(simulation_router)
    app.include_router(export_router)
    app.include_router(tasks_router)
    app.include_router(settings_router)

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "miro-strategy-app"}

    return app
