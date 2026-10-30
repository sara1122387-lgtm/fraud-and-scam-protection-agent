
import json
import sys
from pathlib import Path
from collections import Counter

# Allow importing the project package when this file is run directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.rules import analyze_message


CASES_PATH = PROJECT_ROOT / "tests" / "evaluation_cases.json"


def main():
    with CASES_PATH.open("r", encoding="utf-8") as file:
        cases = json.load(file)

    results = []
    errors = []

    for case in cases:
        try:
            result = analyze_message(case["message"])
            actual = result.get("response")

            if actual is None:
                errors.append(
                    f'{case["id"]}: missing "response" in result'
                )
                continue

            expected = case["expected"]
            passed = actual == expected

            results.append({
                "id": case["id"],
                "expected": expected,
                "actual": actual,
                "passed": passed,
                "score": result.get("score"),
                "signals": result.get("signals", []),
                "explanation": result.get("explanation", ""),
                })

        except Exception as exc:
            errors.append(
                f'{case["id"]}: {type(exc).__name__}: {exc}'
            )

    print("\n=== RULES BASELINE EVALUATION ===")
    print(f"Total cases: {len(cases)}")
    print(f"Evaluated: {len(results)}")
    print(f"Errors: {len(errors)}")

    correct = sum(item["passed"] for item in results)
    incorrect = len(results) - correct

    if results:
        print(f"Exact matches: {correct}/{len(results)}")
        print(f"Agreement: {correct / len(results):.1%}")

    print("\n=== RESULTS BY EXPECTED LABEL ===")
    counts = Counter(
        (item["expected"], item["passed"])
        for item in results
    )

    for label in ("warn", "clarify", "no_clear_indicators"):
        total = sum(
            1 for item in results if item["expected"] == label
        )
        matched = counts[(label, True)]
        print(f"{label}: {matched}/{total} exact matches")

    print("\n=== MISMATCHES ===")
    mismatches = [item for item in results if not item["passed"]]

    if not mismatches:
        print("No classification mismatches.")
    else:
        for item in mismatches:
            print(
                f'\n{item["id"]}: '
                f'expected={item["expected"]}, '
                f'actual={item["actual"]}'
            )
            print(f'Score: {item["score"]}')
            print(f'Signals: {item["signals"]}')
            print(f'Explanation: {item["explanation"]}')

    if errors:
        print("\n=== ERRORS ===")
        for error in errors:
            print(error)

    print("\nNote: context fields are not used by the current rules engine.")
    print("This is a baseline comparison, not proof of real-world accuracy.")


if __name__ == "__main__":
    main()
