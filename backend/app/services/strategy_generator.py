"""Strategy generator — the core service that creates strategic options with win probabilities."""
import json
from sqlalchemy.orm import Session

from app.models.scenario import Scenario
from app.models.competitor import Competitor
from app.models.persona import Persona
from app.models.strategy import Strategy, Tactic, StrategyType, StrategyApproach, Priority
from app.models.framework_analysis import FrameworkAnalysis, FrameworkType
from app.utils.prompt_loader import load_prompt
from app.services.base_service import BaseService


class StrategyGenerator(BaseService):

    async def run(self, scenario_id: str) -> None:
        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            return

        competitors = self.db.query(Competitor).filter(Competitor.scenario_id == scenario_id).all()
        personas = self.db.query(Persona).filter(Persona.scenario_id == scenario_id).all()
        framework_analyses = self.db.query(FrameworkAnalysis).filter(
            FrameworkAnalysis.scenario_id == scenario_id
        ).all()

        # Pull framework summaries
        war_fa = next((f for f in framework_analyses if f.framework_type == FrameworkType.war), None)
        greene_fa = next((f for f in framework_analyses if f.framework_type == FrameworkType.robert_greene), None)
        mbti_fa = next((f for f in framework_analyses if f.framework_type == FrameworkType.mbti), None)

        analysis_summary = self._build_competitor_summary(competitors)
        persona_summary = self._build_persona_summary(personas)
        war_summary = json.loads(war_fa.raw_output) if war_fa and war_fa.raw_output else {}
        greene_summary = json.loads(greene_fa.raw_output) if greene_fa and greene_fa.raw_output else {}
        mbti_summary = json.loads(mbti_fa.raw_output) if mbti_fa and mbti_fa.raw_output else {}

        system = "You are a McKinsey-level strategy consultant. Output only valid JSON array."
        user_prompt = load_prompt(
            "strategy_generation",
            scenario_context=self._build_context(scenario),
            analysis_summary=analysis_summary,
            persona_summary=persona_summary,
            war_strategy_summary=json.dumps(war_summary, indent=2),
            greene_summary=json.dumps(greene_summary, indent=2),
            mbti_summary=json.dumps(mbti_summary, indent=2),
            goals="\n".join(scenario.goals_list()),
            num_strategies=3,
        )

        result = await self.llm.chat_json(system, user_prompt)
        if not isinstance(result, list):
            result = result.get("strategies", []) if isinstance(result, dict) else []

        for item in result:
            strategy = Strategy(
                scenario_id=scenario_id,
                title=item.get("title", "Untitled Strategy"),
                summary=item.get("summary"),
                strategic_objective=item.get("strategic_objective"),
                strategy_type=self._normalize_enum(item.get("strategy_type", "win"), StrategyType),
                approach=self._normalize_enum(item.get("approach", "flanking"), StrategyApproach),
                win_probability=item.get("win_probability"),
                confidence_level=item.get("confidence_level"),
                confidence_interval_lower=item.get("confidence_interval", {}).get("lower"),
                confidence_interval_upper=item.get("confidence_interval", {}).get("upper"),
                frameworks_applied=json.dumps(item.get("frameworks_applied", [])),
                supporting_evidence=json.dumps(item.get("supporting_evidence", [])),
                risks=json.dumps(item.get("risks", [])),
                logic_explanation=item.get("logic_explanation"),
                greene_laws_applied=json.dumps(item.get("greene_laws_applied", [])),
                sun_tzu_principles=json.dumps(item.get("sun_tzu_principles", [])),
            )
            self.db.add(strategy)
            self.db.flush()  # get strategy.id

            # Create tactics
            for t_item in item.get("tactics", []):
                tactic = Tactic(
                    strategy_id=strategy.id,
                    title=t_item.get("title", "Tactic"),
                    description=t_item.get("description"),
                    framework_source=t_item.get("framework_source"),
                    priority=self._normalize_enum(t_item.get("priority", "medium"), Priority),
                    effort=self._normalize_enum(t_item.get("effort", "medium"), Priority),
                    impact=self._normalize_enum(t_item.get("impact", "medium"), Priority),
                    success_metric=t_item.get("success_metric"),
                    greene_law_reference=t_item.get("greene_law_reference"),
                )
                self.db.add(tactic)

        self.db.commit()
        self.logger.info("Strategy generation complete — %d strategies created", len(result))

    def _build_context(self, scenario: Scenario) -> str:
        return "\n\n".join(filter(None, [
            f"Scenario: {scenario.name} ({scenario.scenario_type})",
            f"Industry: {scenario.industry} | Geography: {scenario.geography} | Horizon: {scenario.time_horizon}",
            scenario.description,
            scenario.market_context,
        ]))

    def _build_competitor_summary(self, competitors: list) -> str:
        if not competitors:
            return "No competitors analyzed."
        return "\n".join([
            f"- {c.name}: {c.positioning or 'No positioning'} (threat: {c.threat_level}, CoG: {c.center_of_gravity})"
            for c in competitors
        ])

    def _build_persona_summary(self, personas: list) -> str:
        if not personas:
            return "No personas built yet."
        return "\n".join([
            f"- {p.name} ({p.persona_type}, MBTI: {p.mbti_type}): {p.role}"
            for p in personas
        ])

    def _normalize_enum(self, value: str, enum_class) -> str:
        try:
            return enum_class(value).value
        except ValueError:
            return list(enum_class)[0].value
