"""Competitive analysis service — profiles competitors using Porter's Five Forces + AI."""
import json
from sqlalchemy.orm import Session

from app.models.scenario import Scenario
from app.models.competitor import Competitor
from app.models.framework_analysis import FrameworkAnalysis, FrameworkType
from app.utils.prompt_loader import load_prompt
from app.services.base_service import BaseService


class AnalysisEngine(BaseService):

    async def run(self, scenario_id: str) -> None:
        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            return

        self.logger.info("Running competitive analysis for scenario %s", scenario_id)

        # Build prompt context
        context = self._build_context(scenario)
        # Extract entities from scenario_intake if not already done
        existing_competitors = self.db.query(Competitor).filter(
            Competitor.scenario_id == scenario_id
        ).all()
        competitors_list = (
            [c.name for c in existing_competitors]
            if existing_competitors
            else ["[Auto-identify from scenario context]"]
        )

        system = "You are a competitive intelligence expert. Output only valid JSON."
        user_prompt = load_prompt(
            "competitive_analysis",
            scenario_context=context,
            goals="\n".join(scenario.goals_list()),
            competitors_list="\n".join(competitors_list),
        )

        result = await self.llm.chat_json(system, user_prompt)
        if not isinstance(result, list):
            result = result.get("competitors", []) if isinstance(result, dict) else []

        for item in result:
            existing = self.db.query(Competitor).filter(
                Competitor.scenario_id == scenario_id,
                Competitor.name == item.get("name", ""),
            ).first()
            if existing:
                self._update_competitor(existing, item)
            else:
                comp = Competitor(
                    scenario_id=scenario_id,
                    name=item.get("name", "Unknown"),
                    description=item.get("description"),
                    market_share=item.get("market_share"),
                    strengths=json.dumps(item.get("strengths", [])),
                    weaknesses=json.dumps(item.get("weaknesses", [])),
                    positioning=item.get("positioning"),
                    threat_level=item.get("threat_level"),
                    sentiment_score=item.get("sentiment_score"),
                    center_of_gravity=item.get("center_of_gravity"),
                    mbti_type=item.get("mbti_type"),
                    likely_response=item.get("likely_response_to_our_strategy"),
                    evidence_citations=json.dumps(item.get("evidence_citations", [])),
                )
                self.db.add(comp)

        # Save framework analysis record
        fa = FrameworkAnalysis(
            scenario_id=scenario_id,
            framework_name="Competitive Analysis (Porter's Five Forces)",
            framework_type=FrameworkType.research,
            summary=f"Analyzed {len(result)} competitors/players",
            key_insights=json.dumps([c.get("positioning", "") for c in result[:5]]),
            raw_output=json.dumps(result),
            applicability_score=0.95,
        )
        self.db.add(fa)
        self.db.commit()
        self.logger.info("Competitive analysis complete — %d players profiled", len(result))

    def _build_context(self, scenario: Scenario) -> str:
        parts = [
            f"Scenario: {scenario.name}",
            f"Type: {scenario.scenario_type}",
            f"Industry: {scenario.industry or 'Not specified'}",
            f"Geography: {scenario.geography or 'Not specified'}",
            f"Time Horizon: {scenario.time_horizon or 'Not specified'}",
        ]
        if scenario.description:
            parts.append(f"Description: {scenario.description}")
        if scenario.market_context:
            parts.append(f"Market Context:\n{scenario.market_context}")
        return "\n\n".join(parts)

    def _update_competitor(self, comp: Competitor, data: dict) -> None:
        if data.get("market_share") is not None:
            comp.market_share = data["market_share"]
        if data.get("threat_level"):
            comp.threat_level = data["threat_level"]
        if data.get("positioning"):
            comp.positioning = data["positioning"]
        if data.get("center_of_gravity"):
            comp.center_of_gravity = data["center_of_gravity"]
        if data.get("mbti_type"):
            comp.mbti_type = data["mbti_type"]
