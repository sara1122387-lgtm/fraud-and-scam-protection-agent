
"""Validation for structured context-analyzer results."""

ALLOWED_RESPONSES = {
    "warn",
    "clarify",
    "no_clear_indicators",
}

REQUIRED_FIELDS = {
    "response",
    "situation_type",
    "evidence",
    "reasoning_summary",
    "unknowns",
    "recommended_action",
}


def validate_context_result(data, message):
    """Return validation errors. An empty list means valid."""

    errors = []

    if not isinstance(data, dict):
        return ["The result must be a dictionary."]

    actual_fields = set(data.keys())

    missing_fields = REQUIRED_FIELDS - actual_fields
    extra_fields = actual_fields - REQUIRED_FIELDS

    if missing_fields:
        errors.append(
            f"Missing required fields: {sorted(missing_fields)}"
        )

    if extra_fields:
        errors.append(
            f"Unexpected fields: {sorted(extra_fields)}"
        )

    if missing_fields:
        return errors

    if not isinstance(data["response"], str):
        errors.append("'response' must be a string.")
    elif data["response"] not in ALLOWED_RESPONSES:
        errors.append("Invalid response classification.")

    for field in (
        "situation_type",
        "reasoning_summary",
        "recommended_action",
    ):
        value = data[field]

        if not isinstance(value, str) or not value.strip():
            errors.append(
                f"'{field}' must be a non-empty string."
            )

    for field in ("evidence", "unknowns"):
        value = data[field]

        if not isinstance(value, list):
            errors.append(f"'{field}' must be a list.")
            continue

        if not all(
            isinstance(item, str) and item.strip()
            for item in value
        ):
            errors.append(
                f"Every item in '{field}' must be a non-empty string."
            )

    evidence = data["evidence"]

    if isinstance(evidence, list):
        for item in evidence:
            if isinstance(item, str) and item.strip():
                if item not in message:
                    errors.append(
                        "An evidence excerpt does not appear "
                        "exactly in the supplied message."
                    )
                    break

    if (
        data["response"] == "warn"
        and isinstance(evidence, list)
        and not evidence
    ):
        errors.append(
            "'warn' requires at least one evidence excerpt."
        )

    return errors
