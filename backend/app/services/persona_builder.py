"""Persona builder — generates MBTI-typed psychological personas."""
import json
from sqlalchemy.orm import Session

from app.models.scenario import Scenario
from app.models.persona import Persona, PersonaType
from app.models.framework_analysis import FrameworkAnalysis, FrameworkType
from app.utils.prompt_loader import load_prompt
from app.config import settings
from app.services.base_service import BaseService


class PersonaBuilder(BaseService):

    async def run(self, scenario_id: str) -> None:
        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            return

        existing_count = self.db.query(Persona).filter(Persona.scenario_id == scenario_id).count()
        if existing_count >= settings.strategy_max_personas_to_generate:
            return

        persona_types = ["customer", "opponent", "ally"]
        persona_count = min(settings.strategy_max_personas_to_generate, 6)

        system = "You are a behavioral psychologist and MBTI practitioner. Output only valid JSON array."
        user_prompt = load_prompt(
            "persona_builder",
            scenario_context=self._build_context(scenario),
            goals="\n".join(scenario.goals_list()),
            market_context=scenario.market_context or "",
            persona_count=persona_count,
            persona_types=", ".join(persona_types),
        )

        result = await self.llm.chat_json(system, user_prompt)
        if not isinstance(result, list):
            result = result.get("personas", []) if isinstance(result, dict) else []

        for item in result:
            persona = Persona(
                scenario_id=scenario_id,
                persona_type=item.get("persona_type", "customer"),
                name=item.get("name", "Unknown"),
                age_range=item.get("age_range"),
                role=item.get("role"),
                mbti_type=item.get("mbti_type"),
                mbti_reasoning=item.get("mbti_reasoning"),
                decision_style=item.get("decision_style"),
                stress_reaction=item.get("stress_reaction"),
                motivational_levers=json.dumps(item.get("motivational_levers", [])),
                goals=json.dumps(item.get("goals", [])),
                pain_points=json.dumps(item.get("pain_points", [])),
                motivations=json.dumps(item.get("motivations", [])),
                objections=json.dumps(item.get("objections", [])),
                intent_signals=json.dumps(item.get("intent_signals", [])),
                platform_presence=json.dumps(item.get("platform_presence", {})),
                influence_score=item.get("influence_score"),
                seduction_type=item.get("seduction_type"),
                bio=item.get("bio"),
            )
            self.db.add(persona)

        fa = FrameworkAnalysis(
            scenario_id=scenario_id,
            framework_name="Persona Building (MBTI + Behavioral Psychology)",
            framework_type=FrameworkType.psychology,
            summary=f"Generated {len(result)} MBTI-typed personas",
            key_insights=json.dumps([
                f"{p.get('name')} ({p.get('mbti_type', 'unknown')}): {p.get('role', '')}"
                for p in result[:6]
            ]),
            raw_output=json.dumps(result),
            applicability_score=0.88,
        )
        self.db.add(fa)
        self.db.commit()
        self.logger.info("Persona building complete — %d personas created", len(result))

    def _build_context(self, scenario: Scenario) -> str:
        return "\n\n".join(filter(None, [
            f"Scenario: {scenario.name} ({scenario.scenario_type})",
            scenario.description,
            scenario.market_context,
        ]))
