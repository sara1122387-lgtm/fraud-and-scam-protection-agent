"""Combine deterministic rule findings and contextual AI analysis."""

from copy import deepcopy


ALLOWED_RESPONSES = {
    "warn",
    "clarify",
    "no_clear_indicators",
}


def fuse_evidence(rule_result, context_result=None, context_error=None):
    """
    Combine rule-based and contextual analysis without discarding evidence.

    Rule scores are experimental and are not probabilities.
    A contextual-analysis failure is not treated as a safe result.
    """

    if not isinstance(rule_result, dict):
        raise TypeError("rule_result must be a dictionary")

    if rule_result.get("response") not in ALLOWED_RESPONSES:
        raise ValueError("Invalid rule response classification")

    if not isinstance(rule_result.get("signals"), list):
        raise ValueError("rule_result signals must be a list")

    if context_result is not None and context_error is not None:
        raise ValueError(
            "Provide context_result or context_error, not both"
        )

    if context_result is not None:
        if not isinstance(context_result, dict):
            raise TypeError("context_result must be a dictionary")

        if context_result.get("response") not in ALLOWED_RESPONSES:
            raise ValueError("Invalid context response classification")

        if not isinstance(context_result.get("evidence"), list):
            raise ValueError("context_result evidence must be a list")

    if context_error is not None:
        if not isinstance(context_error, dict):
            raise TypeError("context_error must be a dictionary or None")

        category = context_error.get("category")

        if not isinstance(category, str) or not category.strip():
            raise ValueError(
                "context_error must contain a non-empty category"
            )

    rule_response = rule_result["response"]
    context_available = context_result is not None

    if context_available:
        context_response = context_result["response"]

        if "warn" in (rule_response, context_response):
            final_response = "warn"
        elif "clarify" in (rule_response, context_response):
            final_response = "clarify"
        else:
            final_response = "no_clear_indicators"

        agreement = (
            "full"
            if rule_response == context_response
            else "partial"
        )
    else:
        context_response = None
        final_response = rule_response
        agreement = "unavailable"

    return {
        "response": final_response,
        "rule_analysis": deepcopy(rule_result),
        "context_analysis": (
            deepcopy(context_result)
            if context_result is not None
            else None
        ),
        "context_available": context_available,
        "context_error": deepcopy(context_error),
        "agreement": agreement,
        "disagreement": (
            context_available
            and rule_response != context_response
        ),
        "summary": _build_summary(
            final_response,
            context_available,
        ),
    }


def _build_summary(response, context_available):
    """Build a neutral summary of the combined classification."""

    if response == "warn":
        summary = (
            "تم اكتشاف مؤشرات تستدعي الحذر والتحقق قبل اتخاذ أي إجراء."
        )
    elif response == "clarify":
        summary = (
            "المعلومات الحالية غير كافية للحسم؛ يلزم التحقق من السياق."
        )
    else:
        summary = (
            "لم تكشف مصادر التحليل عن مؤشرات واضحة. "
            "هذا لا يثبت أن الرسالة آمنة."
        )

    if not context_available:
        summary += " التحليل السياقي غير متاح حالياً."

    return summary
