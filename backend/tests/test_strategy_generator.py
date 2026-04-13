"""Tests for StrategyGenerator — verifies win/graceful-exit strategy creation."""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.scenario import Scenario, ScenarioType, ScenarioStatus
from app.services.strategy_generator import StrategyGenerator


MOCK_STRATEGY_RESPONSE = [
    {
        "title": "Flanking Attack — Underserved SMB Segment",
        "summary": "Enter via ignored SMB segment where Rival Corp has no presence.",
        "strategic_objective": "Capture 10% market share in 12 months",
        "strategy_type": "win",
        "approach": "flanking",
        "win_probability": 0.72,
        "confidence_level": "high",
        "confidence_interval": {"lower": 0.58, "upper": 0.84},
        "frameworks_applied": ["Sun Tzu — Attack weakness not strength", "Porter's Five Forces"],
        "supporting_evidence": ["SMB segment has 0 major players", "Price sensitivity studies"],
        "risks": ["Resource constraints", "Brand awareness lag"],
        "logic_explanation": "By targeting the SMB segment Rival Corp ignores, we avoid direct confrontation...",
        "tactics": [
            {
                "title": "Launch SMB-specific pricing tier",
                "framework_source": "marketing",
                "priority": "high",
                "effort": "medium",
                "impact": "high",
                "success_metric": "100 SMB sign-ups in 60 days",
            }
        ],
        "greene_laws_applied": [14, 22],
        "sun_tzu_principles": ["Attack where enemy is unprepared"],
    },
    {
        "title": "Graceful Pivot — Partnership Model",
        "summary": "If direct entry fails, partner with Rival Corp's distributors.",
        "strategic_objective": "Establish distribution channel",
        "strategy_type": "graceful_exit",
        "approach": "co-optation",
        "win_probability": 0.45,
        "confidence_level": "medium",
        "confidence_interval": {"lower": 0.30, "upper": 0.60},
        "frameworks_applied": ["Graceful Exit Framework"],
        "supporting_evidence": [],
        "risks": ["Partner dependency"],
        "logic_explanation": "If win probability falls below 0.4...",
        "tactics": [],
        "greene_laws_applied": [],
        "sun_tzu_principles": [],
    },
]


@pytest.fixture
def mock_scenario():
    return Scenario(
        id="test-scenario-002",
        name="Widget Market Entry",
        description="Strategy test scenario",
        market_context="Competitive widget market",
        goals=json.dumps(["Capture 10% share"]),
        scenario_type=ScenarioType.business,
        status=ScenarioStatus.analyzing,
    )


@pytest.fixture
def mock_db(mock_scenario):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = mock_scenario
    db.query.return_value.filter.return_value.all.return_value = []
    return db


@pytest.mark.asyncio
async def test_strategy_generator_creates_both_paths(mock_db, mock_scenario):
    """StrategyGenerator should create both win and graceful-exit strategies."""
    mock_llm = AsyncMock()
    mock_llm.chat_json = AsyncMock(return_value=MOCK_STRATEGY_RESPONSE)

    gen = StrategyGenerator(db=mock_db, llm=mock_llm)
    await gen.run("test-scenario-002")

    assert mock_db.add.call_count >= 2  # at least 2 strategies + framework analysis


@pytest.mark.asyncio
async def test_strategy_generator_handles_empty(mock_db, mock_scenario):
    """StrategyGenerator should not raise on empty LLM response."""
    mock_llm = AsyncMock()
    mock_llm.chat_json = AsyncMock(return_value=[])

    gen = StrategyGenerator(db=mock_db, llm=mock_llm)
    await gen.run("test-scenario-002")

    mock_db.commit.assert_called()
