
import json
from pathlib import Path

import pytest

from src.rules import analyze_message


SCENARIOS_PATH = Path("data/scenarios.json")


@pytest.fixture
def scenarios():
    return json.loads(
        SCENARIOS_PATH.read_text(encoding="utf-8")
    )


def test_scenarios_file_contains_six_cases(scenarios):
    assert len(scenarios) == 6


def test_scenario_ids_are_unique(scenarios):
    ids = [case["id"] for case in scenarios]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize(
    "scenario_id",
    ["SCN001", "SCN003", "SCN006"],
)
def test_high_risk_scenarios_trigger_warning(
    scenarios,
    scenario_id,
):
    case = next(
        item for item in scenarios
        if item["id"] == scenario_id
    )

    result = analyze_message(case["message_text"])

    assert result["response"] == "warn"
    assert result["score"] >= 4


def test_new_recipient_alone_is_not_enough_to_warn(scenarios):
    case = next(
        item for item in scenarios
        if item["id"] == "SCN002"
    )

    result = analyze_message(case["message_text"])

    assert result["response"] == "no_clear_indicators"
    assert result["signals"] == []


def test_ambiguous_message_requests_clarification(scenarios):
    case = next(
        item for item in scenarios
        if item["id"] == "SCN004"
    )

    result = analyze_message(case["message_text"])

    assert result["response"] == "clarify"


def test_clean_message_does_not_claim_to_be_safe(scenarios):
    case = next(
        item for item in scenarios
        if item["id"] == "SCN005"
    )

    result = analyze_message(case["message_text"])

    assert result["response"] == "no_clear_indicators"
    assert "لا يثبت أن الرسالة آمنة" in result["explanation"]


def test_empty_message_is_rejected():
    with pytest.raises(ValueError):
        analyze_message("   ")


def test_non_string_message_is_rejected():
    with pytest.raises(TypeError):
        analyze_message(None)
