"""Export service — generates PDF and JSON exports of complete scenario analyses."""
import json
import uuid
from pathlib import Path
from sqlalchemy.orm import Session

from app.config import settings
from app.models.scenario import Scenario
from app.models.competitor import Competitor
from app.models.persona import Persona
from app.models.strategy import Strategy, Tactic
from app.models.pain_point import PainPoint
from app.models.campaign import Campaign, KPI
from app.models.roadmap import RoadmapStep
from app.models.framework_analysis import FrameworkAnalysis
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ExportService:
    def __init__(self, db: Session):
        self.db = db

    def export_json(self, scenario_id: str) -> Path:
        data = self._build_export_data(scenario_id)
        export_id = str(uuid.uuid4())[:8]
        path = settings.exports_dir / f"scenario_{scenario_id[:8]}_{export_id}.json"
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("JSON export written to %s", path)
        return path

    def export_pdf(self, scenario_id: str) -> Path:
        data = self._build_export_data(scenario_id)
        markdown = self._build_markdown(data)
        export_id = str(uuid.uuid4())[:8]
        md_path = settings.exports_dir / f"scenario_{scenario_id[:8]}_{export_id}.md"
        pdf_path = settings.exports_dir / f"scenario_{scenario_id[:8]}_{export_id}.pdf"
        md_path.write_text(markdown, encoding="utf-8")
        try:
            import markdown as md_lib
            from weasyprint import HTML
            html = f"<html><body>{md_lib.markdown(markdown)}</body></html>"
            HTML(string=html).write_pdf(str(pdf_path))
            logger.info("PDF export written to %s", pdf_path)
            return pdf_path
        except Exception as e:
            logger.warning("PDF generation failed (%s) — returning markdown file", e)
            return md_path

    def _build_export_data(self, scenario_id: str) -> dict:
        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            return {}

        competitors = self.db.query(Competitor).filter(Competitor.scenario_id == scenario_id).all()
        personas = self.db.query(Persona).filter(Persona.scenario_id == scenario_id).all()
        strategies = self.db.query(Strategy).filter(Strategy.scenario_id == scenario_id).all()
        pain_points = self.db.query(PainPoint).filter(PainPoint.scenario_id == scenario_id).all()
        roadmap = self.db.query(RoadmapStep).filter(RoadmapStep.scenario_id == scenario_id).order_by(
            RoadmapStep.path_type, RoadmapStep.step_number
        ).all()
        frameworks = self.db.query(FrameworkAnalysis).filter(FrameworkAnalysis.scenario_id == scenario_id).all()

        campaigns_data = []
        for strategy in strategies:
            campaigns = self.db.query(Campaign).filter(Campaign.strategy_id == strategy.id).all()
            for campaign in campaigns:
                kpis = self.db.query(KPI).filter(KPI.campaign_id == campaign.id).all()
                campaigns_data.append({**campaign.to_dict(), "kpis": [k.to_dict() for k in kpis]})

        return {
            "scenario": {
                "id": scenario.id,
                "name": scenario.name,
                "type": scenario.scenario_type,
                "status": scenario.status,
                "industry": scenario.industry,
                "geography": scenario.geography,
                "time_horizon": scenario.time_horizon,
                "goals": scenario.goals_list(),
                "description": scenario.description,
            },
            "competitors": [c.to_dict() for c in competitors],
            "personas": [p.to_dict() for p in personas],
            "strategies": [s.to_dict(include_tactics=True) for s in strategies],
            "pain_points": [pp.to_dict() for pp in pain_points],
            "campaigns": campaigns_data,
            "roadmap": [r.to_dict() for r in roadmap],
            "framework_analyses": [f.to_dict() for f in frameworks],
        }

    def _build_markdown(self, data: dict) -> str:
        scenario = data.get("scenario", {})
        lines = [
            f"# {scenario.get('name', 'Strategy Report')}",
            f"**Type:** {scenario.get('type')} | **Industry:** {scenario.get('industry')} | **Horizon:** {scenario.get('time_horizon')}",
            "",
            "## Goals",
            "\n".join(f"- {g}" for g in scenario.get("goals", [])),
            "",
            "## Competitive Analysis",
        ]
        for c in data.get("competitors", []):
            lines.append(f"### {c['name']} (Threat: {c['threat_level']})")
            lines.append(f"**Positioning:** {c.get('positioning', 'N/A')}")
            lines.append(f"**Center of Gravity:** {c.get('center_of_gravity', 'N/A')}")
            lines.append("")

        lines.append("## Personas")
        for p in data.get("personas", []):
            lines.append(f"### {p['name']} ({p['persona_type']}, MBTI: {p.get('mbti_type', 'Unknown')})")
            lines.append(p.get("bio", ""))
            lines.append("")

        lines.append("## Strategies")
        for s in data.get("strategies", []):
            lines.append(f"### {s['title']} ({s['strategy_type'].upper()}) — Win Probability: {(s.get('win_probability') or 0):.0%}")
            lines.append(s.get("summary", ""))
            lines.append("")
            lines.append(s.get("logic_explanation", ""))
            lines.append("")

        lines.append("## Pain Points")
        for pp in data.get("pain_points", []):
            lines.append(f"### {pp['title']} (Severity: {pp['severity']})")
            lines.append(f"**Solution:** {pp.get('proposed_solution', 'N/A')}")
            lines.append("")

        lines.append("## Victory Roadmap")
        for step in data.get("roadmap", []):
            lines.append(f"**Step {step['step_number']} ({step['path_type']}):** {step['title']}")
            lines.append(f"- Probability: {(step.get('probability_of_success') or 0):.0%} | Cumulative: {(step.get('cumulative_probability') or 0):.0%}")
            lines.append("")

        return "\n".join(lines)
