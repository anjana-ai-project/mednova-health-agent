import sys
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.agents.orchestrator import ask

TEST_SET_PATH = Path(__file__).resolve().parent / "test_data" / "multiturn_test_set.json"
RESULTS_PATH = Path(__file__).resolve().parent / "results" / "multiturn_validation.json"


def _truncate(s: str, n: int) -> str:
    s = (s or "").replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"


def _run_thread(thread_index: int, thread: dict) -> dict:
    thread_id = thread["thread_id"]
    turns = thread.get("turns", [])

    turn_results = []
    for i, turn in enumerate(turns, start=1):
        question = turn["question"]
        expected_tool = turn["expected_tool"]
        keyword = turn["validation_keyword"]

        try:
            r = ask(question, thread_id=thread_id)
        except Exception as e:
            turn_results.append({
                "turn": i,
                "question": question,
                "expected_tool": expected_tool,
                "actual_tool": "",
                "tool_match": False,
                "validation_keyword": keyword,
                "keyword_found": False,
                "context_from_turn": turn.get("context_from_turn"),
                "status": "FAIL",
                "reason": f"Exception: {type(e).__name__}: {e}",
                "answer_preview": "",
            })
            continue

        actual_tool = r.get("tool_name", "") or ""
        answer = r.get("answer", "") or ""
        tool_match = actual_tool == expected_tool
        keyword_found = keyword in answer
        status = "PASS" if (tool_match and keyword_found) else "FAIL"

        reasons = []
        if not tool_match:
            reasons.append(f"tool mismatch (got '{actual_tool}')")
        if not keyword_found:
            reasons.append(f"keyword '{keyword}' missing")
        reason = "; ".join(reasons) if reasons else "tool + keyword match"

        turn_results.append({
            "turn": i,
            "question": question,
            "expected_tool": expected_tool,
            "actual_tool": actual_tool,
            "tool_match": tool_match,
            "validation_keyword": keyword,
            "keyword_found": keyword_found,
            "context_from_turn": turn.get("context_from_turn"),
            "status": status,
            "reason": reason,
            "answer_preview": _truncate(answer, 200),
        })

    thread_passed = all(t["status"] == "PASS" for t in turn_results) and bool(turn_results)
    return {
        "thread_index": thread_index,
        "thread_id": thread_id,
        "description": thread.get("description", ""),
        "turns_total": len(turn_results),
        "turns_passed": sum(1 for t in turn_results if t["status"] == "PASS"),
        "status": "PASS" if thread_passed else "FAIL",
        "turns": turn_results,
    }


def run_multiturn_validation() -> dict:
    with open(TEST_SET_PATH, "r", encoding="utf-8") as f:
        threads = json.load(f)

    print(f"Running multi-turn validation on {len(threads)} conversation threads...\n")
    thread_reports = []
    for i, thread in enumerate(threads, start=1):
        print(f"\n--- Thread {i}/{len(threads)}: {thread['thread_id']} ---")
        print(f"    {thread.get('description', '')}")
        report = _run_thread(i, thread)
        for t in report["turns"]:
            print(
                f"  Turn {t['turn']}: {t['status']}  "
                f"tool={t['actual_tool'] or '—'} (expected {t['expected_tool']}); "
                f"keyword '{t['validation_keyword']}' {'found' if t['keyword_found'] else 'missing'}"
            )
        print(f"  Thread result: {report['status']} ({report['turns_passed']}/{report['turns_total']} turns)")
        thread_reports.append(report)

    threads_passed = sum(1 for r in thread_reports if r["status"] == "PASS")
    threads_total = len(thread_reports)
    turns_passed = sum(r["turns_passed"] for r in thread_reports)
    turns_total = sum(r["turns_total"] for r in thread_reports)

    thread_pass_rate = (threads_passed / threads_total) if threads_total else 0.0
    turn_pass_rate = (turns_passed / turns_total) if turns_total else 0.0

    print("\n" + "=" * 70)
    print("Multi-turn Summary")
    print("=" * 70)
    print(f"Threads passed:  {threads_passed}/{threads_total}  ({thread_pass_rate * 100:.1f}%)")
    print(f"Turns passed:    {turns_passed}/{turns_total}  ({turn_pass_rate * 100:.1f}%)")

    report = {
        "threads_total": threads_total,
        "threads_passed": threads_passed,
        "pass_rate": thread_pass_rate,
        "turns_total": turns_total,
        "turns_passed": turns_passed,
        "turn_pass_rate": turn_pass_rate,
        "threads": thread_reports,
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nSaved multi-turn validation results to: {RESULTS_PATH}")

    return report


if __name__ == "__main__":
    run_multiturn_validation()
