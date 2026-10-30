import pytest

from src.analysis_pipeline import analyze_message_with_context
from src.context_analyzer import ContextAnalyzerError


RULE_RESULT = {
    "response": "warn",
    "score": 3,
    "signals": [
        {
            "name": "urgency_pressure",
            "matched_text": "بسرعة",
        }
    ],
    "possible_mixed_input": False,
    "message_only": True,
    "explanation": "Rule-based test result",
}

CONTEXT_RESULT = {
    "response": "warn",
    "situation_type": "suspicious_transfer",
    "evidence": ["بسرعة"],
    "reasoning_summary": "The message applies pressure.",
    "unknowns": ["Sender identity"],
    "recommended_action": "Verify independently.",
}


class FakeAnalyzer:
    """A test analyzer that does not make external API calls."""

    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.received_message = None
        self.received_context = None

    def analyze(self, message, context=None):
        self.received_message = message
        self.received_context = context

        if self.error is not None:
            raise self.error

        return self.result


def test_pipeline_fuses_successful_analyses(monkeypatch):
    import src.analysis_pipeline as pipeline

    monkeypatch.setattr(
        pipeline,
        "analyze_rules",
        lambda message: RULE_RESULT,
    )

    analyzer = FakeAnalyzer(result=CONTEXT_RESULT)

    result = analyze_message_with_context(
        "رسالة تجريبية بسرعة",
        analyzer=analyzer,
    )

    assert result["response"] == "warn"
    assert result["context_available"] is True
    assert result["agreement"] == "full"
    assert result["rule_analysis"] == RULE_RESULT
    assert result["context_analysis"] == CONTEXT_RESULT


def test_pipeline_passes_optional_context(monkeypatch):
    import src.analysis_pipeline as pipeline

    monkeypatch.setattr(
        pipeline,
        "analyze_rules",
        lambda message: RULE_RESULT,
    )

    context = {
        "recipient_is_new": True,
        "transfer_amount": 50000,
    }

    analyzer = FakeAnalyzer(result=CONTEXT_RESULT)

    analyze_message_with_context(
        "رسالة تجريبية",
        context=context,
        analyzer=analyzer,
    )

    assert analyzer.received_message == "رسالة تجريبية"
    assert analyzer.received_context == context


def test_pipeline_preserves_rules_when_analyzer_fails(monkeypatch):
    import src.analysis_pipeline as pipeline

    monkeypatch.setattr(
        pipeline,
        "analyze_rules",
        lambda message: RULE_RESULT,
    )

    analyzer = FakeAnalyzer(
        error=ContextAnalyzerError(
            "Connection unavailable",
            category="connection_error",
        )
    )

    result = analyze_message_with_context(
        "رسالة تجريبية",
        analyzer=analyzer,
    )

    assert result["response"] == "warn"
    assert result["rule_analysis"] == RULE_RESULT
    assert result["context_available"] is False
    assert result["agreement"] == "unavailable"
    assert result["context_error"]["category"] == "connection_error"


def test_pipeline_handles_missing_api_key_during_initialization(
    monkeypatch,
):
    import src.analysis_pipeline as pipeline

    monkeypatch.setattr(
        pipeline,
        "analyze_rules",
        lambda message: RULE_RESULT,
    )

    def fail_to_initialize():
        raise ContextAnalyzerError(
            "API key missing",
            category="missing_api_key",
        )

    monkeypatch.setattr(
        pipeline,
        "ContextAnalyzer",
        fail_to_initialize,
    )

    result = analyze_message_with_context("رسالة تجريبية")

    assert result["response"] == "warn"
    assert result["context_available"] is False
    assert result["context_error"]["category"] == "missing_api_key"


def test_pipeline_does_not_hide_unexpected_programming_errors(
    monkeypatch,
):
    import src.analysis_pipeline as pipeline

    monkeypatch.setattr(
        pipeline,
        "analyze_rules",
        lambda message: RULE_RESULT,
    )

    class BrokenAnalyzer:
        def analyze(self, message, context=None):
            raise RuntimeError("Unexpected programming error")

    with pytest.raises(RuntimeError):
        analyze_message_with_context(
            "رسالة تجريبية",
            analyzer=BrokenAnalyzer(),
        )


def test_pipeline_propagates_rule_validation_errors(monkeypatch):
    import src.analysis_pipeline as pipeline

    def invalid_rules(message):
        raise ValueError("Invalid message")

    monkeypatch.setattr(
        pipeline,
        "analyze_rules",
        invalid_rules,
    )

    analyzer = FakeAnalyzer(result=CONTEXT_RESULT)

    with pytest.raises(ValueError):
        analyze_message_with_context(
            "",
            analyzer=analyzer,
        )

    # Context analysis must not run after rule validation fails.
    assert analyzer.received_message is None


def test_pipeline_does_not_modify_original_results(monkeypatch):
    import src.analysis_pipeline as pipeline

    monkeypatch.setattr(
        pipeline,
        "analyze_rules",
        lambda message: RULE_RESULT,
    )

    analyzer = FakeAnalyzer(result=CONTEXT_RESULT)

    analyze_message_with_context(
        "رسالة تجريبية",
        analyzer=analyzer,
    )

    assert RULE_RESULT["response"] == "warn"
    assert RULE_RESULT["signals"][0]["name"] == "urgency_pressure"
    assert CONTEXT_RESULT["response"] == "warn"
    assert CONTEXT_RESULT["evidence"] == ["بسرعة"]
