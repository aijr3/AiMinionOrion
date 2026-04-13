"""Seed utility — inserts a demo scenario for development smoke testing.

Usage:
    cd backend && python utils/seed.py
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.base import Base, engine, SessionLocal
from app.models.scenario import Scenario, ScenarioType, ScenarioStatus
from app.models.competitor import Competitor


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if demo already exists
    existing = db.query(Scenario).filter(Scenario.name == "Demo: Craft Coffee Market Entry").first()
    if existing:
        print(f"Demo scenario already exists: {existing.id}")
        db.close()
        return

    scenario = Scenario(
        name="Demo: Craft Coffee Market Entry",
        description=(
            "A specialty craft coffee roaster wants to break into the highly competitive "
            "NYC premium coffee market dominated by Blue Bottle and Stumptown. "
            "They have $500k seed funding, a unique single-origin Ethiopian blend, "
            "and relationships with 3 Michelin-star restaurants."
        ),
        market_context=(
            "NYC premium coffee market: ~$2.1B annual revenue, 18% YoY growth. "
            "Blue Bottle holds 28% share, Stumptown 19%, artisan independents 31%, "
            "chains 22%. Consumer trend: ethical sourcing, direct-trade relationships. "
            "TikTok coffee culture is exploding — 'coffee aesthetics' content has 8B views."
        ),
        goals=json.dumps([
            "Capture 3% of NYC premium coffee market within 18 months",
            "Open 2 flagship locations in Brooklyn and Lower East Side",
            "Secure 15 restaurant/hotel wholesale accounts",
            "Build subscription service with 2000 subscribers",
            "Achieve profitability by month 14",
        ]),
        scenario_type=ScenarioType.business,
        industry="Food & Beverage / Specialty Coffee",
        geography="New York City, USA",
        time_horizon="18 months",
        status=ScenarioStatus.created,
    )
    db.add(scenario)
    db.flush()

    # Add seed competitors
    competitors = [
        Competitor(
            scenario_id=scenario.id,
            name="Blue Bottle Coffee",
            description="Premium VC-backed coffee chain with minimalist brand",
            market_share=0.28,
            strengths=json.dumps(["Brand recognition", "Retail footprint", "VC funding", "Media presence"]),
            weaknesses=json.dumps(["High prices", "Corporate feel", "Limited customization"]),
            positioning="Premium aspirational",
            threat_level="high",
            sentiment_score=0.72,
            center_of_gravity="Brand loyalty + physical locations",
            mbti_type="ENTJ",
        ),
        Competitor(
            scenario_id=scenario.id,
            name="Stumptown Coffee Roasters",
            description="Portland-origin craft coffee with strong wholesale network",
            market_share=0.19,
            strengths=json.dumps(["Wholesale relationships", "Quality reputation", "Barista culture"]),
            weaknesses=json.dumps(["Less digital presence", "Aging brand", "Limited NYC locations"]),
            positioning="Authentic craft coffee",
            threat_level="medium",
            sentiment_score=0.68,
            center_of_gravity="Wholesale accounts + barista community",
            mbti_type="ISFP",
        ),
        Competitor(
            scenario_id=scenario.id,
            name="Local Artisan Independents (aggregate)",
            description="50+ independent specialty coffee shops across NYC",
            market_share=0.31,
            strengths=json.dumps(["Community loyalty", "Flexibility", "Authenticity"]),
            weaknesses=json.dumps(["Fragmented", "Limited capital", "No unified brand"]),
            positioning="Neighborhood authenticity",
            threat_level="low",
            sentiment_score=0.81,
            center_of_gravity="Neighborhood community ties",
            mbti_type="INFP",
        ),
    ]
    for c in competitors:
        db.add(c)

    db.commit()
    print(f"Seeded demo scenario: {scenario.id}")
    print(f"  Name: {scenario.name}")
    print(f"  Competitors: {len(competitors)}")
    print(f"\nVisit: http://localhost:3001/scenarios/{scenario.id}/dashboard")
    db.close()


if __name__ == "__main__":
    seed()
