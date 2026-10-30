"""Coordinate rule-based and contextual message analysis."""

from src.rules import analyze_message as analyze_rules
from src.context_analyzer import ContextAnalyzer, ContextAnalyzerError
from src.evidence_fusion import fuse_evidence


def analyze_message_with_context(message, context=None, analyzer=None):
    """
    Run rule-based and contextual analysis, then fuse their evidence.

    The rule-based result is preserved if contextual analysis is unavailable.

    Args:
        message: The original message text.
        context: Optional dictionary containing additional context.
        analyzer: Optional ContextAnalyzer-compatible instance.
                  Injection allows tests to avoid real API calls.

    Returns:
        A unified result produced by fuse_evidence().
    """

    # 1. Deterministic analysis always runs first.
    rule_result = analyze_rules(message)

    # 2. Use an injected analyzer, or create the real one.
    try:
        contextual_analyzer = (
            analyzer if analyzer is not None else ContextAnalyzer()
        )

        context_result = contextual_analyzer.analyze(
            message,
            context=context,
        )

    except ContextAnalyzerError as exc:
        # Preserve rule findings; contextual failure is not evidence of safety.
        context_error = {
            "category": exc.category,
            "message": str(exc),
        }

        return fuse_evidence(
            rule_result=rule_result,
            context_error=context_error,
        )

    # 3. Fuse both successful analyses.
    return fuse_evidence(
        rule_result=rule_result,
        context_result=context_result,
    )
