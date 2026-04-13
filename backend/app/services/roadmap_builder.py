"""Roadmap builder — creates win path and graceful forward path with cumulative probabilities."""
import json
from sqlalchemy.orm import Session

from app.models.scenario import Scenario
from app.models.strategy import Strategy
from app.models.campaign import Campaign
from app.models.persona import Persona
from app.models.roadmap import RoadmapStep, PathType
from app.utils.prompt_loader import load_prompt
from app.services.base_service import BaseService


class RoadmapBuilder(BaseService):

    async def run(self, scenario_id: str) -> None:
        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            return

        strategies = self.db.query(Strategy).filter(Strategy.scenario_id == scenario_id).all()
        campaigns = self.db.query(Campaign).all()  # all campaigns linked to this scenario's strategies
        personas = self.db.query(Persona).filter(Persona.scenario_id == scenario_id).all()

        strategy_summaries = [{"title": s.title, "type": s.strategy_type, "probability": s.win_probability} for s in strategies]
        campaign_summaries = [{"name": c.name, "objective": c.objective, "aida_phase": c.aida_phase} for c in campaigns[:10]]
        persona_obstacles = [{"name": p.name, "mbti": p.mbti_type, "objections": json.loads(p.objections or "[]")[:3]} for p in personas]

        system = "You are a strategic execution expert and probability theorist. Output only valid JSON."
        user_prompt = load_prompt(
            "roadmap_builder",
            scenario_context=self._build_context(scenario),
            strategy_summaries=json.dumps(strategy_summaries, indent=2),
            campaign_summaries=json.dumps(campaign_summaries, indent=2),
            persona_obstacles=json.dumps(persona_obstacles, indent=2),
        )

        result = await self.llm.chat_json(system, user_prompt)
        if not isinstance(result, dict):
            return

        for path_key, path_type in [("win_path", PathType.win), ("graceful_forward_path", PathType.graceful_forward)]:
            steps = result.get(path_key, [])
            for step_data in steps:
                step = RoadmapStep(
                    scenario_id=scenario_id,
                    step_number=step_data.get("step_number", 0),
                    path_type=path_type,
                    title=step_data.get("title", "Step"),
                    description=step_data.get("description"),
                    milestone=step_data.get("milestone"),
                    probability_of_success=step_data.get("probability_of_success"),
                    cumulative_probability=step_data.get("cumulative_probability"),
                    probability_rationale=step_data.get("probability_rationale"),
                    dependencies=json.dumps(step_data.get("dependencies", [])),
                    owner=step_data.get("owner"),
                    estimated_duration=step_data.get("estimated_duration"),
                    risk_factors=json.dumps(step_data.get("risk_factors", [])),
                )
                self.db.add(step)

        self.db.commit()
        win_steps = len(result.get("win_path", []))
        gf_steps = len(result.get("graceful_forward_path", []))
        self.logger.info("Roadmap built — %d win steps, %d graceful forward steps", win_steps, gf_steps)

    def _build_context(self, scenario: Scenario) -> str:
        return "\n\n".join(filter(None, [
            f"Scenario: {scenario.name} ({scenario.scenario_type})",
            scenario.description,
            scenario.market_context,
        ]))
