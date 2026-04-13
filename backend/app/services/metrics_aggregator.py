"""Metrics aggregator — computes dashboard metrics across campaigns, KPIs, and strategies."""
import json
from sqlalchemy.orm import Session

from app.models.scenario import Scenario
from app.models.strategy import Strategy
from app.models.campaign import Campaign, KPI, KpiSnapshot
from app.models.roadmap import RoadmapStep
from app.models.framework_analysis import FrameworkAnalysis
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MetricsAggregator:
    def __init__(self, db: Session):
        self.db = db

    async def run(self, scenario_id: str) -> None:
        """No-op run for pipeline compatibility — metrics are computed on demand."""
        pass

    def get_dashboard(self, scenario_id: str) -> dict:
        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            return {}

        strategies = self.db.query(Strategy).filter(Strategy.scenario_id == scenario_id).all()
        framework_analyses = self.db.query(FrameworkAnalysis).filter(
            FrameworkAnalysis.scenario_id == scenario_id
        ).all()

        all_campaigns = []
        for strategy in strategies:
            campaigns = self.db.query(Campaign).filter(Campaign.strategy_id == strategy.id).all()
            all_campaigns.extend(campaigns)

        campaign_data = []
        total_budget = 0
        for campaign in all_campaigns:
            kpis = self.db.query(KPI).filter(KPI.campaign_id == campaign.id).all()
            kpi_data = []
            for kpi in kpis:
                snapshots = self.db.query(KpiSnapshot).filter(
                    KpiSnapshot.kpi_id == kpi.id
                ).order_by(KpiSnapshot.recorded_at.asc()).all()
                kpi_data.append({
                    **kpi.to_dict(),
                    "history": [s.to_dict() for s in snapshots],
                })
            if campaign.budget:
                total_budget += campaign.budget
            campaign_data.append({**campaign.to_dict(), "kpis": kpi_data})

        win_steps = self.db.query(RoadmapStep).filter(
            RoadmapStep.scenario_id == scenario_id,
            RoadmapStep.path_type == "win",
        ).order_by(RoadmapStep.step_number.desc()).first()

        top_strategy = max(strategies, key=lambda s: s.win_probability or 0, default=None)

        return {
            "scenario_id": scenario_id,
            "status": scenario.status,
            "overall_win_probability": top_strategy.win_probability if top_strategy else None,
            "confidence_interval": {
                "lower": top_strategy.confidence_interval_lower if top_strategy else None,
                "upper": top_strategy.confidence_interval_upper if top_strategy else None,
            },
            "final_cumulative_probability": win_steps.cumulative_probability if win_steps else None,
            "total_strategies": len(strategies),
            "total_campaigns": len(all_campaigns),
            "total_budget": total_budget,
            "frameworks_applied": len(framework_analyses),
            "campaigns": campaign_data,
            "framework_summaries": [
                {
                    "name": fa.framework_name,
                    "type": fa.framework_type,
                    "summary": fa.summary,
                    "score": fa.applicability_score,
                }
                for fa in framework_analyses
            ],
        }
