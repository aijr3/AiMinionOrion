"""Robert Greene framework analyzer — applies the full Greene library to every scenario."""
import json
from sqlalchemy.orm import Session

from app.models.scenario import Scenario
from app.models.competitor import Competitor
from app.models.persona import Persona
from app.models.framework_analysis import FrameworkAnalysis, FrameworkType
from app.utils.prompt_loader import load_prompt
from app.services.base_service import BaseService


class RobertGreeneAnalyzer(BaseService):
    """
    Applies Robert Greene's complete library:
    - The 48 Laws of Power
    - The 33 Strategies of War
    - The Art of Seduction (9 seducer types)
    - The Laws of Human Nature (18 laws)
    - Mastery (3 phases)
    - The 50th Law (fearlessness)
    - The Daily Laws
    """

    async def run(self, scenario_id: str) -> None:
        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            return

        competitors = self.db.query(Competitor).filter(Competitor.scenario_id == scenario_id).all()
        personas = self.db.query(Persona).filter(Persona.scenario_id == scenario_id).all()

        key_players = [
            {"name": c.name, "type": "competitor", "positioning": c.positioning}
            for c in competitors
        ] + [
            {"name": p.name, "type": p.persona_type, "role": p.role}
            for p in personas
        ]

        competitive_position = ", ".join([
            f"{c.name} (threat: {c.threat_level}, sentiment: {c.sentiment_score})"
            for c in competitors
        ]) or "No competitive analysis yet"

        system = "You are a Robert Greene scholar. Apply his complete works to this scenario. Output only valid JSON."
        user_prompt = load_prompt(
            "robert_greene_overlay",
            scenario_context=self._build_context(scenario),
            key_players=json.dumps(key_players, indent=2),
            goals="\n".join(scenario.goals_list()),
            competitive_position=competitive_position,
        )

        result = await self.llm.chat_json(system, user_prompt)

        key_insights = []
        if isinstance(result, dict):
            lop = result.get("laws_of_power", {})
            rec_laws = lop.get("recommended_laws_for_us", [])
            for law in rec_laws[:3]:
                key_insights.append(
                    f"Law {law.get('law_number')}: {law.get('law_name')} — {law.get('tactical_application', '')[:80]}"
                )
            mastery = result.get("mastery_assessment", {})
            if mastery.get("current_phase"):
                key_insights.append(f"Mastery Phase: {mastery['current_phase']} — {mastery.get('phase_recommendation', '')[:80]}")
            law50 = result.get("fiftieth_law", {})
            if law50.get("fear_assessment"):
                key_insights.append(f"50th Law: {law50['fear_assessment'][:100]}")

        fa = FrameworkAnalysis(
            scenario_id=scenario_id,
            framework_name="Robert Greene Complete Framework (48 Laws + 33 Strategies + Art of Seduction + Human Nature + Mastery + 50th Law)",
            framework_type=FrameworkType.robert_greene,
            summary="Applied Robert Greene's full library: 48 Laws of Power, 33 Strategies of War, Art of Seduction, Laws of Human Nature, Mastery phases, and 50th Law fearlessness assessment",
            key_insights=json.dumps(key_insights),
            raw_output=json.dumps(result) if isinstance(result, dict) else "{}",
            applicability_score=0.92,
        )
        self.db.add(fa)
        self.db.commit()
        self.logger.info("Robert Greene analysis complete for scenario %s", scenario_id)

    def _build_context(self, scenario: Scenario) -> str:
        return "\n\n".join(filter(None, [
            f"Scenario: {scenario.name} ({scenario.scenario_type})",
            f"Industry: {scenario.industry}",
            f"Geography: {scenario.geography}",
            scenario.description,
            scenario.market_context,
        ]))
