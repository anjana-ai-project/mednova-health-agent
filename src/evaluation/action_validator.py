import sys
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.agents.orchestrator import ask

TEST_SET_PATH = Path(__file__).resolve().parent / "test_data" / "agent_test_set.json"
RESULTS_PATH = Path(__file__).resolve().parent / "results" / "action_validation.json"


def _truncate(s: str, n: int) -> str:
    s = (s or "").replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"


def _validate_case(index: int, case: dict) -> dict:
    question = case["question"]
    expected_tool = case["expected_tool"]
    expected_key = case["expected_data_key"]

    try:
        r = ask(question, thread_id=f"eval_action_{index}")
    except Exception as e:
        return {
            "index": index,
            "question": question,
            "domain": case.get("domain", ""),
            "expected_tool": expected_tool,
            "actual_tool": "",
            "tool_match": False,
            "expected_data_key": expected_key,
            "data_in_answer": False,
            "status": "FAIL",
            "reason": f"Exception: {type(e).__name__}: {e}",
            "answer_preview": "",
        }

    actual_tool = r.get("tool_name", "") or ""
    answer = r.get("answer", "") or ""
    tool_match = actual_tool == expected_tool
    data_in_answer = expected_key in answer
    status = "PASS" if (tool_match and data_in_answer) else "FAIL"

    reasons = []
    if not tool_match:
        reasons.append(f"tool mismatch (got '{actual_tool}')")
    if not data_in_answer:
        reasons.append(f"'{expected_key}' missing from answer")
    reason = "; ".join(reasons) if reasons else "tool + data match"

    return {
        "index": index,
        "question": question,
        "domain": case.get("domain", ""),
        "expected_tool": expected_tool,
        "actual_tool": actual_tool,
        "tool_match": tool_match,
        "expected_data_key": expected_key,
        "data_in_answer": data_in_answer,
        "status": status,
        "reason": reason,
        "answer_preview": _truncate(answer, 200),
    }


def run_action_validation(max_cases: int | None = None) -> dict:
    with open(TEST_SET_PATH, "r", encoding="utf-8") as f:
        cases = json.load(f)
    if max_cases is not None:
        cases = cases[:max_cases]

    print(f"Running action validation on {len(cases)} agent test cases (end-to-end via orchestrator)...\n")
    results = []
    for i, case in enumerate(cases):
        print(f"  [{i + 1}/{len(cases)}] {case['question']}")
        results.append(_validate_case(i, case))

    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    pass_rate = (passed / total) if total else 0.0

    header = f"\n{'question':<42} {'expected_tool':<32} {'actual_tool':<32} {'data_in_answer':<14} status"
    print(header)
    print("-" * len(header))
    for r in results:
        print(
            f"{_truncate(r['question'], 40):<42} "
            f"{r['expected_tool']:<32} "
            f"{(r['actual_tool'] or '—'):<32} "
            f"{str(r['data_in_answer']):<14} "
            f"{r['status']}"
        )

    print("\nFailures:")
    failures = [r for r in results if r["status"] == "FAIL"]
    if not failures:
        print("  (none)")
    else:
        for f in failures:
            print(f"  - [{f['domain']}] {f['expected_tool']} :: {f['reason']}")

    by_domain: dict = {}
    for r in results:
        d = r["domain"]
        by_domain.setdefault(d, {"passed": 0, "total": 0})
        by_domain[d]["total"] += 1
        if r["status"] == "PASS":
            by_domain[d]["passed"] += 1

    print("\nDomain breakdown:")
    for d, counts in sorted(by_domain.items()):
        rate = counts["passed"] / counts["total"] if counts["total"] else 0.0
        print(f"  {d:<11} {counts['passed']}/{counts['total']}  ({rate * 100:.1f}%)")

    print(f"\nOverall pass rate: {passed}/{total} ({pass_rate * 100:.1f}%)")

    report = {
        "total": total,
        "passed": passed,
        "pass_rate": pass_rate,
        "by_domain": {
            d: {**c, "pass_rate": c["passed"] / c["total"] if c["total"] else 0.0}
            for d, c in by_domain.items()
        },
        "results": results,
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nSaved action validation results to: {RESULTS_PATH}")

    return report


if __name__ == "__main__":
    run_action_validation(max_cases=1)
