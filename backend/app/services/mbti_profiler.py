"""MBTI profiling service — infers and applies MBTI types to all key players."""
import json
from sqlalchemy.orm import Session

from app.models.scenario import Scenario
from app.models.competitor import Competitor
from app.models.persona import Persona
from app.models.framework_analysis import FrameworkAnalysis, FrameworkType
from app.utils.prompt_loader import load_prompt
from app.services.base_service import BaseService


class MBTIProfiler(BaseService):

    async def run(self, scenario_id: str) -> None:
        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            return

        competitors = self.db.query(Competitor).filter(Competitor.scenario_id == scenario_id).all()
        entities = [{"name": c.name, "type": "competitor", "description": c.description or c.positioning or ""} for c in competitors]

        if not entities:
            self.logger.info("No entities to MBTI-profile for scenario %s", scenario_id)
            return

        system = "You are a certified Myers-Briggs practitioner. Output only valid JSON."
        user_prompt = load_prompt(
            "mbti_analysis",
            scenario_context=self._build_context(scenario),
            entities_list=json.dumps(entities, indent=2),
        )

        result = await self.llm.chat_json(system, user_prompt)
        if not isinstance(result, list):
            result = []

        # Update competitors with MBTI data
        for item in result:
            name = item.get("entity_name", "")
            comp = next((c for c in competitors if c.name.lower() == name.lower()), None)
            if comp and item.get("mbti_type"):
                comp.mbti_type = item["mbti_type"]

        fa = FrameworkAnalysis(
            scenario_id=scenario_id,
            framework_name="MBTI Psychological Profiling",
            framework_type=FrameworkType.mbti,
            summary=f"Profiled {len(result)} entities with MBTI types",
            key_insights=json.dumps([f"{r.get('entity_name')}: {r.get('mbti_type')} — {r.get('communication_approach', '')}" for r in result]),
            raw_output=json.dumps(result),
            applicability_score=0.85,
        )
        self.db.add(fa)
        self.db.commit()
        self.logger.info("MBTI profiling complete for scenario %s", scenario_id)

    def _build_context(self, scenario: Scenario) -> str:
        parts = [scenario.name, scenario.description or "", scenario.market_context or ""]
        return "\n\n".join(p for p in parts if p)
