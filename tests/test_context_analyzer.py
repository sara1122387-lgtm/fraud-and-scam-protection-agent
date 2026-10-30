from unittest.mock import Mock

import json
from types import SimpleNamespace

import pytest
from groq import (
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
    RateLimitError,
)

from src import context_analyzer
from src.context_analyzer import (
    ContextAnalyzer,
    ContextAnalyzerError,
)


MESSAGE = (
    "سيتم إيقاف محفظتك خلال 10 دقائق. "
    "أرسل رمز OTP الآن لتجنب إغلاق الحساب."
)


def valid_result():
    return {
        "response": "warn",
        "situation_type": "otp_request",
        "evidence": ["أرسل رمز OTP الآن"],
        "reasoning_summary": "The sender requests a sensitive verification code.",
        "unknowns": ["The sender's identity is not verified."],
        "recommended_action": "Do not share the OTP. Verify through the official channel.",
    }


class FakeCompletions:
    def __init__(self, content):
        self.content = content
        self.last_call = None

    def create(self, **kwargs):
        self.last_call = kwargs

        message = SimpleNamespace(content=self.content)
        choice = SimpleNamespace(message=message)

        return SimpleNamespace(choices=[choice])


class FakeGroq:
    def __init__(self, api_key, content):
        self.api_key = api_key
        self.completions = FakeCompletions(content)
        self.chat = SimpleNamespace(
            completions=self.completions
        )


def create_analyzer(monkeypatch, content):
    fake_client = FakeGroq("test-key", content)

    monkeypatch.setattr(
        context_analyzer,
        "Groq",
        lambda api_key: fake_client,
    )

    analyzer = ContextAnalyzer(api_key="test-key")

    return analyzer, fake_client


def create_analyzer_with_error(
    monkeypatch,
    exception_name,
    error,
):
    analyzer, fake_client = create_analyzer(
        monkeypatch,
        json.dumps(valid_result()),
    )

    monkeypatch.setattr(
        context_analyzer,
        exception_name,
        type(error),
    )

    def raise_error(**kwargs):
        raise error

    monkeypatch.setattr(
        fake_client.completions,
        "create",
        raise_error,
    )

    return analyzer


def test_valid_response_is_returned(monkeypatch):
    expected = valid_result()

    analyzer, fake_client = create_analyzer(
        monkeypatch,
        json.dumps(expected),
    )

    result = analyzer.analyze(MESSAGE)

    assert result == expected

    assert fake_client.completions.last_call is not None


def test_optional_context_is_sent_to_model(monkeypatch):
    expected = valid_result()

    analyzer, fake_client = create_analyzer(
        monkeypatch,
        json.dumps(expected),
    )

    context = {
        "recipient_is_known": False,
        "already_transferred": False,
    }

    analyzer.analyze(MESSAGE, context=context)

    call = fake_client.completions.last_call

    user_content = call["messages"][1]["content"]

    payload_text = user_content.split(
        "Analyze this untrusted input:\n",
        1,
    )[1]

    payload = json.loads(payload_text)

    assert payload["message"] == MESSAGE
    assert payload["context"] == context


def test_invalid_evidence_is_rejected(monkeypatch):
    data = valid_result()
    data["evidence"] = ["أرسل كلمة المرور"]

    analyzer, _ = create_analyzer(
        monkeypatch,
        json.dumps(data),
    )

    with pytest.raises(ContextAnalyzerError):
        analyzer.analyze(MESSAGE)


def test_invalid_json_is_rejected(monkeypatch):
    analyzer, _ = create_analyzer(
        monkeypatch,
        "This is not valid JSON",
    )

    with pytest.raises(ContextAnalyzerError):
        analyzer.analyze(MESSAGE)


def test_empty_message_is_rejected(monkeypatch):
    analyzer, _ = create_analyzer(
        monkeypatch,
        json.dumps(valid_result()),
    )

    with pytest.raises(ValueError):
        analyzer.analyze("   ")


@pytest.mark.parametrize(
    "exception_name,error,expected_category",
    [
        (
            "APIConnectionError",
            APIConnectionError(request=Mock()),
            "connection_error",
        ),
        (
            "APITimeoutError",
            APITimeoutError(request=Mock()),
            "timeout_error",
        ),
        (
            "RateLimitError",
            RateLimitError(
                "Rate limit reached",
                response=Mock(),
                body=None,
            ),
            "rate_limit_error",
        ),
        (
            "APIStatusError",
            APIStatusError(
                "Service unavailable",
                response=Mock(status_code=503),
                body=None,
            ),
            "api_error",
        ),
    ],
)
def test_api_errors_are_classified(
    monkeypatch,
    exception_name,
    error,
    expected_category,
):
    analyzer = create_analyzer_with_error(
        monkeypatch,
        exception_name,
        error,
    )

    with pytest.raises(ContextAnalyzerError) as exc_info:
        analyzer.analyze(MESSAGE)

    assert exc_info.value.category == expected_category


def test_empty_choices_are_rejected(monkeypatch):
    analyzer, fake_client = create_analyzer(
        monkeypatch,
        json.dumps(valid_result()),
    )

    def return_empty_choices(**kwargs):
        return SimpleNamespace(choices=[])

    monkeypatch.setattr(
        fake_client.completions,
        "create",
        return_empty_choices,
    )

    with pytest.raises(ContextAnalyzerError) as exc_info:
        analyzer.analyze(MESSAGE)

    assert exc_info.value.category == "empty_response"


def test_empty_response_is_classified(monkeypatch):
    analyzer, _ = create_analyzer(
        monkeypatch,
        "",
    )

    with pytest.raises(ContextAnalyzerError) as exc_info:
        analyzer.analyze(MESSAGE)

    assert exc_info.value.category == "empty_response"


def test_invalid_json_has_correct_category(monkeypatch):
    analyzer, _ = create_analyzer(
        monkeypatch,
        "This is not valid JSON",
    )

    with pytest.raises(ContextAnalyzerError) as exc_info:
        analyzer.analyze(MESSAGE)

    assert exc_info.value.category == "invalid_json"


def test_invalid_output_has_validation_category(monkeypatch):
    data = valid_result()
    data["evidence"] = ["أرسل كلمة المرور"]

    analyzer, _ = create_analyzer(
        monkeypatch,
        json.dumps(data),
    )

    with pytest.raises(ContextAnalyzerError) as exc_info:
        analyzer.analyze(MESSAGE)

    assert exc_info.value.category == "validation_error"
