"""Campaign planner — structures Google Ads-compatible AIDA campaigns."""
import json
from sqlalchemy.orm import Session

from app.models.scenario import Scenario
from app.models.strategy import Strategy
from app.models.persona import Persona
from app.models.competitor import Competitor
from app.models.campaign import Campaign, KPI, AidaPhase, CampaignStatus, MeasurementFrequency
from app.utils.prompt_loader import load_prompt
from app.services.base_service import BaseService


class CampaignPlanner(BaseService):

    async def run(self, scenario_id: str) -> None:
        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            return

        strategies = self.db.query(Strategy).filter(Strategy.scenario_id == scenario_id).all()
        if not strategies:
            return

        personas = self.db.query(Persona).filter(Persona.scenario_id == scenario_id).all()
        competitors = self.db.query(Competitor).filter(Competitor.scenario_id == scenario_id).all()

        # Plan campaigns for top strategy (highest win probability)
        top_strategy = sorted(strategies, key=lambda s: s.win_probability or 0, reverse=True)[0]

        system = "You are a Google Ads-certified performance marketing director. Output only valid JSON array."
        user_prompt = load_prompt(
            "campaign_planner",
            strategy_detail=json.dumps(top_strategy.to_dict(include_tactics=True), indent=2),
            time_horizon=scenario.time_horizon or "6 months",
            persona_names_and_types="\n".join([f"{p.name} ({p.persona_type}, {p.mbti_type})" for p in personas]),
            competitive_context="\n".join([f"{c.name}: {c.positioning}" for c in competitors]),
        )

        result = await self.llm.chat_json(system, user_prompt)
        if not isinstance(result, list):
            result = result.get("campaigns", []) if isinstance(result, dict) else []

        for item in result:
            campaign = Campaign(
                strategy_id=top_strategy.id,
                name=item.get("name", "Campaign"),
                objective=item.get("objective"),
                aida_phase=self._normalize(item.get("aida_phase", "awareness"), AidaPhase),
                campaign_type=item.get("campaign_type"),
                channels=json.dumps(item.get("channels", [])),
                google_ads_compatible=item.get("google_ads_compatible", False),
                key_messages=json.dumps(item.get("key_messages", [])),
                owner=item.get("owner"),
                start_date=item.get("start_date"),
                end_date=item.get("end_date"),
                budget=item.get("budget_estimate"),
                status=CampaignStatus.planned,
                success_definition=item.get("success_definition"),
            )
            self.db.add(campaign)
            self.db.flush()

            for kpi_item in item.get("kpis", []):
                kpi = KPI(
                    campaign_id=campaign.id,
                    name=kpi_item.get("name", "KPI"),
                    target_value=kpi_item.get("target_value"),
                    unit=kpi_item.get("unit"),
                    measurement_frequency=self._normalize(
                        kpi_item.get("measurement_frequency", "weekly"), MeasurementFrequency
                    ),
                )
                self.db.add(kpi)

        self.db.commit()
        self.logger.info("Campaign planning complete — %d campaigns created", len(result))

    def _normalize(self, value: str, enum_class) -> str:
        try:
            return enum_class(value).value
        except ValueError:
            return list(enum_class)[0].value
