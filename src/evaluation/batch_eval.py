import sys
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.evaluation.action_validator import run_action_validation
from src.evaluation.negative_validator import run_negative_validation
from src.evaluation.multiturn_validator import run_multiturn_validation
from src.evaluation.batch_llm_judge import run_batch_llm_judge

RESULTS_PATH = Path(__file__).resolve().parent / "results" / "batch_report.json"


def main() -> dict:
    print("=" * 70)
    print("MedNova Health Agent — Full Batch Evaluation")
    print("=" * 70)

    print("\n[1/4] Action validation\n" + "-" * 70)
    action = run_action_validation()

    print("\n[2/4] Negative validation\n" + "-" * 70)
    negative = run_negative_validation()

    print("\n[3/4] Multi-turn validation\n" + "-" * 70)
    multiturn = run_multiturn_validation()

    print("\n[4/4] LLM-as-Judge batch\n" + "-" * 70)
    judge = run_batch_llm_judge()

    judge_summary = {
        set_name: {
            "answer_quality": rep["averages"]["answer_quality"],
            "faithfulness": rep["averages"]["faithfulness"],
            "relevancy": rep["averages"]["relevancy"],
            "routing_correct_rate": rep["averages"]["routing_correct_rate"],
            "scored_cases": rep["averages"]["scored_cases"],
            "total_cases": rep["averages"]["total_cases"],
        }
        for set_name, rep in judge.items()
    }

    summary = {
        "action_pass_rate": action["pass_rate"],
        "action_passed": action["passed"],
        "action_total": action["total"],
        "negative_pass_rate": negative["pass_rate"],
        "negative_passed": negative["passed"],
        "negative_total": negative["total"],
        "multiturn_pass_rate": multiturn["pass_rate"],
        "multiturn_threads_passed": multiturn["threads_passed"],
        "multiturn_threads_total": multiturn["threads_total"],
        "multiturn_turn_pass_rate": multiturn["turn_pass_rate"],
        "llm_judge": judge_summary,
    }

    print("\n" + "=" * 70)
    print("Combined Report")
    print("=" * 70)
    print(
        f"Action validation:       {summary['action_passed']}/{summary['action_total']} "
        f"({summary['action_pass_rate'] * 100:.1f}%)"
    )
    print(
        f"Negative validation:     {summary['negative_passed']}/{summary['negative_total']} "
        f"({summary['negative_pass_rate'] * 100:.1f}%)"
    )
    print(
        f"Multi-turn (threads):    {summary['multiturn_threads_passed']}/{summary['multiturn_threads_total']} "
        f"({summary['multiturn_pass_rate'] * 100:.1f}%)"
    )
    print(
        f"Multi-turn (turns):      {summary['multiturn_turn_pass_rate'] * 100:.1f}%"
    )
    print("LLM-as-Judge averages:")
    print(f"  {'set':<10} {'answer_q':<10} {'faithful':<10} {'relevancy':<10} route_ok%")
    for set_name, s in judge_summary.items():
        print(
            f"  {set_name:<10} {s['answer_quality']:<10.2f} {s['faithfulness']:<10.2f} "
            f"{s['relevancy']:<10.2f} {s['routing_correct_rate'] * 100:.1f}"
        )
    print("=" * 70)

    combined = {
        "action_validation": action,
        "negative_validation": negative,
        "multiturn_validation": multiturn,
        "llm_judge": judge,
        "summary": summary,
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)
    print(f"\nSaved combined batch report to: {RESULTS_PATH}")

    return combined


if __name__ == "__main__":
    main()
