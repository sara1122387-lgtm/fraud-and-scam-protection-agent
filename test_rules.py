
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


def test_relative_impersonation_with_urgent_transfer_is_detected():
    message = (
        "اني ابن عمك، تلفوني راح ينطفي، "
        "حوللي فلوس هسه ولا تتصل بي."
    )

    result = analyze_message(message)

        # Regression test for relative impersonation and transfer pressure.
    assert result["response"] == "warn"


def test_safe_account_transfer_scam_is_detected():
    message = (
        "حول فلوسك لهذا الحساب الآمن حتى نحمي رصيدك "
        "من الاختراق، ولا تتأخر."
    )

    result = analyze_message(message)

        # Regression test for relative impersonation and transfer pressure.
    assert result["response"] == "warn"


def test_fake_prize_requesting_financial_information_is_detected():
    message = (
        "مبروك ربحت جائزة، افتح الرابط وأرسل معلومات بطاقتك "
        "حتى تستلم المكافأة."
    )

    result = analyze_message(message)

    assert result["response"] == "warn"


def test_warning_about_otp_is_not_mistaken_for_a_credential_request():
    message = (
        "لا تشارك رمز التحقق مع أي شخص، "
        "حتى لو ادعى أنه موظف دعم."
    )

    result = analyze_message(message)

    # A protective warning should not be classified as high risk
    # merely because it mentions an OTP.
    assert result["response"] != "warn"
