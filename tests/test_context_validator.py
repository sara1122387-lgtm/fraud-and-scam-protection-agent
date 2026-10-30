
import pytest

from src.context_validator import validate_context_result


MESSAGE = (
    "سيتم إيقاف محفظتك خلال 10 دقائق. "
    "أرسل رمز OTP الآن لتجنب إغلاق الحساب."
)


def valid_result():
    return {
        "response": "warn",
        "situation_type": "financial_scam",
        "evidence": ["أرسل رمز OTP الآن"],
        "reasoning_summary": (
            "The message requests a sensitive authentication code "
            "and uses an urgent threat."
        ),
        "unknowns": ["The sender's identity is unverified."],
        "recommended_action": (
            "Do not share the code. Verify through an official channel."
        ),
    }


def test_valid_result_passes():
    assert validate_context_result(
        valid_result(), MESSAGE
    ) == []


def test_missing_field_is_rejected():
    data = valid_result()
    del data["unknowns"]

    errors = validate_context_result(data, MESSAGE)

    assert any("Missing required fields" in e for e in errors)


def test_extra_field_is_rejected():
    data = valid_result()
    data["confidence"] = 0.99

    errors = validate_context_result(data, MESSAGE)

    assert any("Unexpected fields" in e for e in errors)


def test_invalid_response_is_rejected():
    data = valid_result()
    data["response"] = "safe"

    errors = validate_context_result(data, MESSAGE)

    assert any("Invalid response classification" in e for e in errors)


def test_evidence_not_in_message_is_rejected():
    data = valid_result()
    data["evidence"] = ["أرسل كلمة المرور"]

    errors = validate_context_result(data, MESSAGE)

    assert any("does not appear exactly" in e for e in errors)


def test_wrong_field_type_is_rejected():
    data = valid_result()
    data["unknowns"] = "sender not verified"

    errors = validate_context_result(data, MESSAGE)

    assert any("'unknowns' must be a list" in e for e in errors)


def test_warning_without_evidence_is_rejected():
    data = valid_result()
    data["evidence"] = []

    errors = validate_context_result(data, MESSAGE)

    assert any("'warn' requires at least one evidence excerpt" in e
               for e in errors)


def test_empty_reasoning_is_rejected():
    data = valid_result()
    data["reasoning_summary"] = "   "

    errors = validate_context_result(data, MESSAGE)

    assert any("'reasoning_summary' must be a non-empty string."
               in e for e in errors)


@pytest.mark.parametrize(
    "classification",
    ["warn", "clarify", "no_clear_indicators"],
)
def test_all_allowed_classifications_can_pass(classification):
    data = valid_result()
    data["response"] = classification

    errors = validate_context_result(data, MESSAGE)

    assert errors == []
