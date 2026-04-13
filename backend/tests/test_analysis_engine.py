"""Tests for AnalysisEngine — verifies competitor extraction and framework recording."""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.scenario import Scenario, ScenarioType, ScenarioStatus
from app.models.competitor import Competitor
from app.models.framework_analysis import FrameworkAnalysis
from app.services.analysis_engine import AnalysisEngine


MOCK_COMPETITOR_RESPONSE = [
    {
        "name": "Rival Corp",
        "description": "Primary competitor in the space",
        "market_share": 0.35,
        "strengths": ["Brand recognition", "Distribution network"],
        "weaknesses": ["Legacy tech", "High prices"],
        "positioning": "Premium established player",
        "threat_level": "high",
        "sentiment_score": 0.6,
        "center_of_gravity": "Brand loyalty",
        "mbti_type": "ENTJ",
        "likely_response_to_our_strategy": "Price competition",
        "evidence_citations": ["Industry report Q4 2024"],
    }
]


@pytest.fixture
def mock_scenario():
    s = Scenario(
        id="test-scenario-001",
        name="Test Market Entry",
        description="Entering the widget market",
        market_context="Competitive widget market with 3 major players",
        goals=json.dumps(["Capture 10% market share", "Launch in 6 months"]),
        scenario_type=ScenarioType.business,
        industry="Manufacturing",
        status=ScenarioStatus.analyzing,
    )
    return s


@pytest.fixture
def mock_db(mock_scenario):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = mock_scenario
    db.query.return_value.filter.return_value.all.return_value = []
    return db


@pytest.mark.asyncio
async def test_analysis_engine_creates_competitors(mock_db, mock_scenario):
    """AnalysisEngine should create competitor records from LLM response."""
    mock_llm = AsyncMock()
    mock_llm.chat_json = AsyncMock(return_value=MOCK_COMPETITOR_RESPONSE)

    engine = AnalysisEngine(db=mock_db, llm=mock_llm)
    await engine.run("test-scenario-001")

    mock_db.add.assert_called()
    mock_db.commit.assert_called()


@pytest.mark.asyncio
async def test_analysis_engine_handles_empty_response(mock_db, mock_scenario):
    """AnalysisEngine should handle empty LLM response gracefully."""
    mock_llm = AsyncMock()
    mock_llm.chat_json = AsyncMock(return_value=[])

    engine = AnalysisEngine(db=mock_db, llm=mock_llm)
    await engine.run("test-scenario-001")

    # Should not raise; framework analysis record still gets added
    mock_db.commit.assert_called()


@pytest.mark.asyncio
async def test_analysis_engine_handles_dict_response(mock_db, mock_scenario):
    """AnalysisEngine should unwrap competitors from dict-wrapped response."""
    mock_llm = AsyncMock()
    mock_llm.chat_json = AsyncMock(
        return_value={"competitors": MOCK_COMPETITOR_RESPONSE}
    )

    engine = AnalysisEngine(db=mock_db, llm=mock_llm)
    await engine.run("test-scenario-001")

    mock_db.add.assert_called()
