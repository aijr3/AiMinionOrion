"""MiroFish simulation bridge — seeds MiroFish with scenario data and retrieves predictions."""
import sys
import json
from sqlalchemy.orm import Session

from app.config import settings
from app.models.scenario import Scenario
from app.models.competitor import Competitor
from app.models.persona import Persona
from app.models.task import Task, TaskStatus
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SimulationBridge:
    """
    Integrates with the MiroFish multi-agent simulation engine.
    MiroFish is mounted as a git submodule at mirofish/.
    Its backend is added to sys.path to allow direct imports.
    """

    def __init__(self, db: Session):
        self.db = db
        self._ensure_mirofish_path()

    def _ensure_mirofish_path(self):
        path = settings.mirofish_backend_path
        if path not in sys.path:
            sys.path.insert(0, path)

    async def run_simulation(self, scenario_id: str, task_id: str) -> dict:
        if not settings.mirofish_simulation_enabled:
            return {"status": "disabled", "message": "MiroFish simulation is disabled in config"}

        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            return {"status": "error", "message": "Scenario not found"}

        task = self.db.query(Task).filter(Task.id == task_id).first()

        try:
            # Import MiroFish components
            from app.services.simulation_manager import SimulationManager  # type: ignore
            from app.services.oasis_profile_generator import OasisProfileGenerator  # type: ignore
        except ImportError as e:
            logger.warning("MiroFish not available: %s", e)
            return {"status": "unavailable", "message": str(e)}

        try:
            competitors = self.db.query(Competitor).filter(Competitor.scenario_id == scenario_id).all()
            personas = self.db.query(Persona).filter(Persona.scenario_id == scenario_id).all()

            # Build seed document
            seed_doc = self._build_seed_document(scenario, competitors, personas)

            # Generate OASIS profiles
            profile_gen = OasisProfileGenerator()
            profiles = await profile_gen.generate_profiles(
                seed_document=seed_doc,
                num_agents=min(20, len(competitors) + len(personas) + 5),
            )

            # Launch simulation
            sim_manager = SimulationManager()
            project_id = await sim_manager.prepare_simulation(
                profiles=profiles,
                simulation_requirement=f"Strategy scenario: {scenario.name}. Goals: {', '.join(scenario.goals_list())}",
            )

            # Update scenario with MiroFish project reference
            scenario.mirofish_project_id = project_id
            if task:
                task.status = TaskStatus.processing
                task.progress = 30
                task.message = "MiroFish simulation launched..."
            self.db.commit()

            return {"status": "launched", "project_id": project_id}

        except Exception as e:
            logger.error("MiroFish simulation failed: %s", e)
            if task:
                task.status = TaskStatus.failed
                task.error = str(e)
                self.db.commit()
            return {"status": "error", "message": str(e)}

    def _build_seed_document(self, scenario: Scenario, competitors: list, personas: list) -> str:
        lines = [
            f"# Strategic Scenario: {scenario.name}",
            f"**Type:** {scenario.scenario_type}",
            f"**Industry:** {scenario.industry}",
            f"**Geography:** {scenario.geography}",
            f"**Time Horizon:** {scenario.time_horizon}",
            "",
            "## Context",
            scenario.market_context or scenario.description or "",
            "",
            "## Goals",
            "\n".join(f"- {g}" for g in scenario.goals_list()),
            "",
            "## Key Players",
        ]
        for c in competitors:
            lines.append(f"### {c.name} (Competitor)")
            lines.append(f"- Position: {c.positioning}")
            lines.append(f"- Threat: {c.threat_level}")
            lines.append(f"- MBTI: {c.mbti_type}")
        for p in personas:
            lines.append(f"### {p.name} ({p.persona_type})")
            lines.append(f"- Role: {p.role}")
            lines.append(f"- MBTI: {p.mbti_type}")
        return "\n".join(lines)

    async def get_simulation_results(self, scenario_id: str) -> dict:
        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario or not scenario.mirofish_project_id:
            return {"status": "no_simulation"}

        try:
            from app.services.report_agent import ReportAgent  # type: ignore
            report_agent = ReportAgent()
            report = await report_agent.generate_report(scenario.mirofish_project_id)
            scenario.mirofish_report = json.dumps(report) if isinstance(report, dict) else str(report)
            self.db.commit()
            return {"status": "complete", "report": report}
        except Exception as e:
            logger.error("Failed to fetch MiroFish results: %s", e)
            return {"status": "error", "message": str(e)}
