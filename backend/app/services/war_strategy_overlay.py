"""War strategy overlay — applies Sun Tzu, Clausewitz, and OODA to the scenario."""
import json
from sqlalchemy.orm import Session

from app.models.scenario import Scenario
from app.models.competitor import Competitor
from app.models.framework_analysis import FrameworkAnalysis, FrameworkType
from app.utils.prompt_loader import load_prompt
from app.services.base_service import BaseService


class WarStrategyOverlay(BaseService):

    async def run(self, scenario_id: str) -> None:
        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            return

        competitors = self.db.query(Competitor).filter(Competitor.scenario_id == scenario_id).all()
        competitor_profiles = json.dumps([c.to_dict() for c in competitors], indent=2)

        system = "You are a military strategist expert in Sun Tzu, Clausewitz, and Boyd's OODA loop. Output only valid JSON."
        user_prompt = load_prompt(
            "war_strategy_overlay",
            scenario_context=self._build_context(scenario),
            competitor_profiles=competitor_profiles,
            goals="\n".join(scenario.goals_list()),
        )

        result = await self.llm.chat_json(system, user_prompt)

        key_insights = []
        if isinstance(result, dict):
            ooda = result.get("ooda_analysis", {})
            if ooda.get("decide"):
                key_insights.append(f"OODA Decision: {ooda['decide']}")
            cw = result.get("clausewitz_analysis", {})
            if cw.get("center_of_gravity"):
                key_insights.append(f"Center of Gravity: {cw['center_of_gravity']}")
            if result.get("recommended_strategies"):
                key_insights.extend(result["recommended_strategies"][:3])

        fa = FrameworkAnalysis(
            scenario_id=scenario_id,
            framework_name="War Strategy (Sun Tzu + Clausewitz + OODA)",
            framework_type=FrameworkType.war,
            summary="Applied Art of War, Clausewitz center-of-gravity, and OODA loop analysis",
            key_insights=json.dumps(key_insights),
            raw_output=json.dumps(result) if isinstance(result, dict) else "{}",
            applicability_score=0.90,
        )
        self.db.add(fa)
        self.db.commit()
        self.logger.info("War strategy overlay complete for scenario %s", scenario_id)

    def _build_context(self, scenario: Scenario) -> str:
        return "\n\n".join(filter(None, [
            f"Scenario: {scenario.name} ({scenario.scenario_type})",
            scenario.description,
            scenario.market_context,
        ]))
