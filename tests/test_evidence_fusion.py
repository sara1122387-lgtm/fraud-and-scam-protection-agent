import pytest

from src.evidence_fusion import fuse_evidence


@pytest.fixture
def warning_rules():
    return {
        "response": "warn",
        "score": 4,
        "signals": [
            {
                "name": "credential_request",
                "weight": 4,
                "matched_phrase": "رمز التحقق",
            }
        ],
        "possible_mixed_input": False,
        "message_only": True,
        "explanation": "ظهرت مؤشرات تستدعي الحذر.",
    }


@pytest.fixture
def no_indicator_rules():
    return {
        "response": "no_clear_indicators",
        "score": 0,
        "signals": [],
        "possible_mixed_input": False,
        "message_only": True,
        "explanation": "لم تظهر مؤشرات واضحة.",
    }


@pytest.fixture
def warning_context():
    return {
        "response": "warn",
        "situation_type": "credential_request",
        "evidence": ["ارسل رمز التحقق"],
        "reasoning_summary": "توجد مطالبة بمعلومات تحقق حساسة.",
        "unknowns": ["هوية المرسل غير معروفة."],
        "recommended_action": "لا تشارك رمز التحقق وتحقق من الجهة عبر قناة رسمية.",
    }


@pytest.fixture
def clarify_context():
    return {
        "response": "clarify",
        "situation_type": "ambiguous_request",
        "evidence": [],
        "reasoning_summary": "السياق غير كافٍ للحسم.",
        "unknowns": ["هوية المرسل غير معروفة."],
        "recommended_action": "تحقق من هوية المرسل.",
    }


@pytest.fixture
def no_indicator_context():
    return {
        "response": "no_clear_indicators",
        "situation_type": "ordinary_message",
        "evidence": [],
        "reasoning_summary": "لم تظهر مؤشرات واضحة في النص.",
        "unknowns": ["لا تتوفر معلومات مستقلة عن المرسل."],
        "recommended_action": "تحقق من المرسل عند الشك.",
    }


def test_both_sources_warn(warning_rules, warning_context):
    result = fuse_evidence(warning_rules, warning_context)

    assert result["response"] == "warn"
    assert result["agreement"] == "full"
    assert result["disagreement"] is False
    assert result["context_available"] is True


def test_rule_warning_is_preserved_when_context_finds_no_indicators(
    warning_rules,
    no_indicator_context,
):
    result = fuse_evidence(warning_rules, no_indicator_context)

    assert result["response"] == "warn"
    assert result["disagreement"] is True
    assert result["rule_analysis"]["signals"] == warning_rules["signals"]


def test_context_warning_is_preserved_without_rule_signals(
    no_indicator_rules,
    warning_context,
):
    result = fuse_evidence(no_indicator_rules, warning_context)

    assert result["response"] == "warn"
    assert result["disagreement"] is True


def test_clarify_and_warn_produce_warning(
    warning_rules,
    clarify_context,
):
    result = fuse_evidence(warning_rules, clarify_context)

    assert result["response"] == "warn"
    assert result["disagreement"] is True


def test_both_sources_clarify(
    no_indicator_rules,
    clarify_context,
):
    rules = {
        **no_indicator_rules,
        "response": "clarify",
    }

    result = fuse_evidence(rules, clarify_context)

    assert result["response"] == "clarify"
    assert result["agreement"] == "full"


def test_both_sources_find_no_clear_indicators(
    no_indicator_rules,
    no_indicator_context,
):
    result = fuse_evidence(no_indicator_rules, no_indicator_context)

    assert result["response"] == "no_clear_indicators"
    assert result["agreement"] == "full"
    assert "لا يثبت" in result["summary"]


def test_groq_failure_preserves_rule_warning(warning_rules):
    error = {
        "category": "timeout_error",
        "message": "The request timed out.",
    }

    result = fuse_evidence(
        warning_rules,
        context_error=error,
    )

    assert result["response"] == "warn"
    assert result["context_available"] is False
    assert result["context_error"] == error
    assert result["agreement"] == "unavailable"


def test_groq_failure_does_not_mean_safe(no_indicator_rules):
    error = {
        "category": "connection_error",
        "message": "Could not connect to the API.",
    }

    result = fuse_evidence(
        no_indicator_rules,
        context_error=error,
    )

    assert result["response"] == "no_clear_indicators"
    assert result["context_available"] is False
    assert "لا يثبت" in result["summary"]


def test_original_results_are_not_modified(
    warning_rules,
    warning_context,
):
    original_rules = {
        **warning_rules,
        "signals": [dict(signal) for signal in warning_rules["signals"]],
    }
    original_context = dict(warning_context)

    fuse_evidence(original_rules, original_context)

    assert original_rules == warning_rules
    assert original_context == warning_context


def test_invalid_rule_result_type():
    with pytest.raises(TypeError):
        fuse_evidence(None)


def test_invalid_rule_response():
    with pytest.raises(ValueError):
        fuse_evidence({"response": "safe"})


def test_invalid_context_response(warning_rules):
    invalid_context = {"response": "safe"}

    with pytest.raises(ValueError):
        fuse_evidence(warning_rules, invalid_context)


def test_cannot_provide_context_result_and_error_together(
    warning_rules,
    warning_context,
):
    with pytest.raises(ValueError):
        fuse_evidence(
            warning_rules,
            context_result=warning_context,
            context_error={"category": "timeout_error"},
        )


def test_invalid_rule_signals_type():
    with pytest.raises(ValueError):
        fuse_evidence({
            "response": "warn",
            "signals": None,
        })


def test_invalid_context_evidence_type(warning_rules):
    with pytest.raises(ValueError):
        fuse_evidence(
            warning_rules,
            {
                "response": "warn",
                "evidence": None,
            },
        )


def test_context_error_requires_category(warning_rules):
    with pytest.raises(ValueError):
        fuse_evidence(
            warning_rules,
            context_error={"message": "Request failed"},
        )


def test_context_unavailable_is_mentioned_when_rules_warn(
    warning_rules,
):
    result = fuse_evidence(
        warning_rules,
        context_error={"category": "timeout_error"},
    )

    assert result["response"] == "warn"
    assert "غير متاح" in result["summary"]


def test_nested_results_are_independent(
    warning_rules,
    warning_context,
):
    result = fuse_evidence(warning_rules, warning_context)

    result["rule_analysis"]["signals"][0]["name"] = "modified"
    result["context_analysis"]["evidence"].append("modified")

    assert warning_rules["signals"][0]["name"] == "credential_request"
    assert warning_context["evidence"] == ["ارسل رمز التحقق"]
