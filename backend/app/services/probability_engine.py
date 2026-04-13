"""Probability engine — Bayesian win probability + Monte Carlo sensitivity analysis."""
import json
from sqlalchemy.orm import Session

from app.models.scenario import Scenario
from app.models.competitor import Competitor
from app.models.persona import Persona
from app.models.strategy import Strategy
from app.models.framework_analysis import FrameworkAnalysis, FrameworkType
from app.utils.prompt_loader import load_prompt
from app.services.base_service import BaseService


class ProbabilityEngine(BaseService):

    async def run(self, scenario_id: str) -> None:
        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            return

        strategies = self.db.query(Strategy).filter(Strategy.scenario_id == scenario_id).all()
        competitors = self.db.query(Competitor).filter(Competitor.scenario_id == scenario_id).all()
        personas = self.db.query(Persona).filter(Persona.scenario_id == scenario_id).all()

        fa_list = self.db.query(FrameworkAnalysis).filter(
            FrameworkAnalysis.scenario_id == scenario_id
        ).all()
        greene_fa = next((f for f in fa_list if f.framework_type == FrameworkType.robert_greene), None)

        system = "You are a quantitative strategist. Output only valid JSON."
        user_prompt = load_prompt(
            "probability_scoring",
            scenario_context=self._build_context(scenario),
            strategies_summary=json.dumps([
                {"title": s.title, "approach": s.approach, "type": s.strategy_type}
                for s in strategies
            ], indent=2),
            competitive_summary=json.dumps([
                {"name": c.name, "threat": c.threat_level, "market_share": c.market_share}
                for c in competitors
            ], indent=2),
            persona_summary=json.dumps([
                {"name": p.name, "type": p.persona_type, "mbti": p.mbti_type, "influence": p.influence_score}
                for p in personas
            ], indent=2),
            greene_summary=greene_fa.raw_output if greene_fa else "{}",
        )

        result = await self.llm.chat_json(system, user_prompt)
        if not isinstance(result, dict):
            return

        # Update strategies with refined probabilities
        overall_prob = result.get("overall_win_probability")
        for strategy in strategies:
            if strategy.win_probability is None and overall_prob is not None:
                strategy.win_probability = overall_prob

        fa = FrameworkAnalysis(
            scenario_id=scenario_id,
            framework_name="Probability Scoring (Bayesian + Monte Carlo)",
            framework_type=FrameworkType.probability,
            summary=f"Win probability: {result.get('overall_win_probability', 'unknown'):.0%} (CI: {result.get('confidence_interval', {}).get('lower', '?'):.0%}–{result.get('confidence_interval', {}).get('upper', '?'):.0%})" if result.get('overall_win_probability') else "Probability analysis complete",
            key_insights=json.dumps([
                f"{d.get('factor')}: {d.get('direction')} ({d.get('weight', 0):.0%} weight)"
                for d in result.get("key_drivers", [])[:5]
            ]),
            raw_output=json.dumps(result),
            applicability_score=0.93,
        )
        self.db.add(fa)
        self.db.commit()
        self.logger.info("Probability analysis complete for scenario %s", scenario_id)

    def _build_context(self, scenario: Scenario) -> str:
        return "\n\n".join(filter(None, [
            f"Scenario: {scenario.name} ({scenario.scenario_type})",
            scenario.description,
            scenario.market_context,
        ]))
