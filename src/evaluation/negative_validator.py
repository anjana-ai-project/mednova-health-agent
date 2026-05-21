import sys
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.agents.orchestrator import ask

TEST_SET_PATH = Path(__file__).resolve().parent / "test_data" / "negative_test_set.json"
RESULTS_PATH = Path(__file__).resolve().parent / "results" / "negative_validation.json"


def _truncate(s: str, n: int) -> str:
    s = (s or "").replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"


def _validate_case(index: int, case: dict) -> dict:
    question = case["question"]
    category = case["category"]
    refusal_keywords = case.get("refusal_keywords", [])
    must_not_contain = case.get("must_not_contain", [])

    try:
        r = ask(question, thread_id=f"eval_neg_{index}")
    except Exception as e:
        return {
            "index": index,
            "category": category,
            "question": question,
            "refusal_found": False,
            "safe_response": False,
            "status": "FAIL",
            "reason": f"Exception: {type(e).__name__}: {e}",
            "matched_refusal_keyword": None,
            "leaked_strings": [],
            "answer_preview": "",
        }

    answer = r.get("answer", "") or ""
    answer_lower = answer.lower()

    matched_kw = next((kw for kw in refusal_keywords if kw.lower() in answer_lower), None)
    refusal_found = matched_kw is not None

    leaked = [s for s in must_not_contain if s.lower() in answer_lower]
    safe_response = len(leaked) == 0

    status = "PASS" if (refusal_found and safe_response) else "FAIL"

    reasons = []
    if not refusal_found:
        reasons.append(f"no refusal keyword found (looked for {refusal_keywords})")
    if not safe_response:
        reasons.append(f"leaked unsafe content: {leaked}")
    reason = "; ".join(reasons) if reasons else "refused safely"

    return {
        "index": index,
        "category": category,
        "question": question,
        "expected_behavior": case.get("expected_behavior", ""),
        "refusal_found": refusal_found,
        "matched_refusal_keyword": matched_kw,
        "safe_response": safe_response,
        "leaked_strings": leaked,
        "status": status,
        "reason": reason,
        "answer_preview": _truncate(answer, 200),
    }


def run_negative_validation() -> dict:
    with open(TEST_SET_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)

    print(f"Running negative validation on {len(cases)} adversarial / out-of-scope / nonexistent cases...\n")
    results = []
    for i, case in enumerate(cases):
        print(f"  [{i + 1}/{len(cases)}] [{case['category']}] {case['question']}")
        results.append(_validate_case(i, case))

    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    pass_rate = (passed / total) if total else 0.0

    header = f"\n{'category':<18} {'question':<42} {'refusal_found':<14} {'safe_response':<14} status"
    print(header)
    print("-" * len(header))
    for r in results:
        print(
            f"{r['category']:<18} "
            f"{_truncate(r['question'], 40):<42} "
            f"{str(r['refusal_found']):<14} "
            f"{str(r['safe_response']):<14} "
            f"{r['status']}"
        )

    print("\nFailures:")
    failures = [r for r in results if r["status"] == "FAIL"]
    if not failures:
        print("  (none)")
    else:
        for f in failures:
            print(f"  - [{f['category']}] {f['question']!r} :: {f['reason']}")

    by_category: dict = {}
    for r in results:
        c = r["category"]
        by_category.setdefault(c, {"passed": 0, "total": 0})
        by_category[c]["total"] += 1
        if r["status"] == "PASS":
            by_category[c]["passed"] += 1

    print("\nCategory breakdown:")
    for c, counts in sorted(by_category.items()):
        rate = counts["passed"] / counts["total"] if counts["total"] else 0.0
        print(f"  {c:<18} {counts['passed']}/{counts['total']}  ({rate * 100:.1f}%)")

    print(f"\nOverall pass rate: {passed}/{total} ({pass_rate * 100:.1f}%)")

    report = {
        "total": total,
        "passed": passed,
        "pass_rate": pass_rate,
        "by_category": {
            c: {**counts, "pass_rate": counts["passed"] / counts["total"] if counts["total"] else 0.0}
            for c, counts in by_category.items()
        },
        "results": results,
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nSaved negative validation results to: {RESULTS_PATH}")

    return report


if __name__ == "__main__":
    run_negative_validation()
