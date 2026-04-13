"""Pain point extractor — surfaces friction and obstacles using psychological + strategic lenses."""
import json
from sqlalchemy.orm import Session

from app.models.scenario import Scenario
from app.models.competitor import Competitor
from app.models.persona import Persona
from app.models.strategy import Strategy
from app.models.pain_point import PainPoint, Severity, PainCategory
from app.utils.prompt_loader import load_prompt
from app.services.base_service import BaseService


class PainPointExtractor(BaseService):

    async def run(self, scenario_id: str) -> None:
        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            return

        strategies = self.db.query(Strategy).filter(Strategy.scenario_id == scenario_id).all()
        personas = self.db.query(Persona).filter(Persona.scenario_id == scenario_id).all()
        competitors = self.db.query(Competitor).filter(Competitor.scenario_id == scenario_id).all()

        system = "You are a business process consultant and organizational psychologist. Output only valid JSON array."
        user_prompt = load_prompt(
            "pain_point_extraction",
            scenario_context=self._build_context(scenario),
            strategy_summaries="\n".join([f"- {s.title}: {s.summary}" for s in strategies]),
            persona_summaries="\n".join([f"- {p.name} ({p.mbti_type}): {p.role}" for p in personas]),
            competitive_summary="\n".join([f"- {c.name} (threat: {c.threat_level})" for c in competitors]),
        )

        result = await self.llm.chat_json(system, user_prompt)
        if not isinstance(result, list):
            result = result.get("pain_points", []) if isinstance(result, dict) else []

        for item in result:
            # Map persona names to IDs
            affected_ids = []
            for pname in item.get("affected_personas", []):
                persona = next((p for p in personas if p.name.lower() == pname.lower()), None)
                if persona:
                    affected_ids.append(persona.id)

            pp = PainPoint(
                scenario_id=scenario_id,
                title=item.get("title", "Pain Point"),
                description=item.get("description"),
                severity=self._normalize(item.get("severity", "medium"), Severity),
                category=self._normalize(item.get("category", "process"), PainCategory),
                affected_persona_ids=json.dumps(affected_ids),
                root_cause=item.get("root_cause"),
                proposed_solution=item.get("proposed_solution"),
                effort_to_fix=item.get("effort_to_fix"),
                if_unresolved_impact=item.get("if_unresolved_impact"),
            )
            self.db.add(pp)

        self.db.commit()
        self.logger.info("Pain point extraction complete — %d pain points identified", len(result))

    def _build_context(self, scenario: Scenario) -> str:
        return "\n\n".join(filter(None, [
            f"Scenario: {scenario.name} ({scenario.scenario_type})",
            scenario.description,
            scenario.market_context,
        ]))

    def _normalize(self, value: str, enum_class) -> str:
        try:
            return enum_class(value).value
        except ValueError:
            return list(enum_class)[0].value
