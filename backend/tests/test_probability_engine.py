"""Tests for ProbabilityEngine — Bayesian + Monte Carlo probability scoring."""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models.scenario import Scenario, ScenarioType, ScenarioStatus
from app.models.strategy import Strategy, StrategyType, StrategyApproach
from app.services.probability_engine import ProbabilityEngine


MOCK_PROBABILITY_RESPONSE = {
    "strategies": [
        {
            "strategy_id": "strat-001",
            "bayesian_win_probability": 0.68,
            "monte_carlo_mean": 0.65,
            "monte_carlo_p10": 0.42,
            "monte_carlo_p90": 0.85,
            "confidence_interval": {"lower": 0.52, "upper": 0.78},
            "confidence_level": "high",
            "key_variables": [
                {"variable": "Market adoption speed", "impact": "high", "current_assumption": "moderate"},
                {"variable": "Competitor response", "impact": "high", "current_assumption": "delayed"},
            ],
            "sensitivity_notes": "Win probability is most sensitive to competitor response timing.",
        }
    ]
}


@pytest.fixture
def mock_scenario():
    return Scenario(
        id="test-scenario-003",
        name="Probability Test",
        market_context="Widget market",
        goals=json.dumps(["Win"]),
        scenario_type=ScenarioType.business,
        status=ScenarioStatus.analyzing,
    )


@pytest.fixture
def mock_strategy():
    return Strategy(
        id="strat-001",
        scenario_id="test-scenario-003",
        title="Flanking Attack",
        strategy_type=StrategyType.win,
        approach=StrategyApproach.flanking,
        win_probability=0.60,
    )


@pytest.fixture
def mock_db(mock_scenario, mock_strategy):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = mock_scenario
    db.query.return_value.filter.return_value.all.return_value = [mock_strategy]
    return db


@pytest.mark.asyncio
async def test_probability_engine_updates_strategies(mock_db, mock_scenario):
    """ProbabilityEngine should update win_probability on strategy records."""
    mock_llm = AsyncMock()
    mock_llm.chat_json = AsyncMock(return_value=MOCK_PROBABILITY_RESPONSE)

    engine = ProbabilityEngine(db=mock_db, llm=mock_llm)
    await engine.run("test-scenario-003")

    mock_db.commit.assert_called()


@pytest.mark.asyncio
async def test_probability_engine_handles_no_strategies(mock_db, mock_scenario):
    """ProbabilityEngine should exit gracefully when no strategies exist."""
    mock_db.query.return_value.filter.return_value.all.return_value = []
    mock_llm = AsyncMock()
    mock_llm.chat_json = AsyncMock(return_value={})

    engine = ProbabilityEngine(db=mock_db, llm=mock_llm)
    await engine.run("test-scenario-003")

    # Should not raise
