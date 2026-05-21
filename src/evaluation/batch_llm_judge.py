import sys
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.agents.orchestrator import ask
from src.evaluation.evaluator import evaluate_response

AGENT_PATH = Path(__file__).resolve().parent / "test_data" / "agent_test_set.json"
NEG_PATH = Path(__file__).resolve().parent / "test_data" / "negative_test_set.json"
RAG_PATH = Path(__file__).resolve().parent / "test_data" / "rag_test_set.json"
RESULTS_PATH = Path(__file__).resolve().parent / "results" / "batch_llm_judge.json"


def _safe_float(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _judge_set(set_name: str, cases: list) -> dict:
    print(f"\n--- LLM-as-Judge on {set_name} ({len(cases)} cases) ---")
    per_case = []
    for i, case in enumerate(cases):
        q = case["question"]
        print(f"  [{i + 1}/{len(cases)}] {q}")
        entry = {
            "index": i,
            "question": q,
            "answer": "",
            "agent_route": "",
            "sources": [],
            "scores": None,
            "error": None,
        }
        try:
            r = ask(q, thread_id=f"judge_{set_name}_{i}")
            answer = r.get("answer", "") or ""
            agent_route = r.get("agent_route", "") or ""
            sources = r.get("sources", []) or []
            entry["answer"] = answer
            entry["agent_route"] = agent_route
            entry["sources"] = sources

            scores = evaluate_response(q, answer, agent_route, sources)
            entry["scores"] = scores
        except Exception as e:
            entry["error"] = f"{type(e).__name__}: {e}"

        per_case.append(entry)

    aq, ff, rel, routing_ok = [], [], [], []
    for entry in per_case:
        s = entry.get("scores")
        if not s:
            continue
        aq.append(_safe_float(s.get("answer_quality", 0)))
        ff.append(_safe_float(s.get("faithfulness", 0)))
        rel.append(_safe_float(s.get("relevancy", 0)))
        routing_ok.append(1 if s.get("routing_correct") else 0)

    n = len(aq)
    def avg(xs):
        return sum(xs) / len(xs) if xs else 0.0

    averages = {
        "answer_quality": avg(aq),
        "faithfulness": avg(ff),
        "relevancy": avg(rel),
        "routing_correct_rate": avg(routing_ok),
        "scored_cases": n,
        "total_cases": len(cases),
    }

    print(
        f"  Averages — answer_quality: {averages['answer_quality']:.2f}, "
        f"faithfulness: {averages['faithfulness']:.2f}, "
        f"relevancy: {averages['relevancy']:.2f}, "
        f"routing_correct: {averages['routing_correct_rate'] * 100:.1f}%  "
        f"(scored {n}/{len(cases)})"
    )

    return {"averages": averages, "per_case": per_case}


def run_batch_llm_judge() -> dict:
    with open(AGENT_PATH, "r", encoding="utf-8") as f:
        agent_cases = json.load(f)
    with open(NEG_PATH, "r", encoding="utf-8") as f:
        negative_cases = json.load(f)
    with open(RAG_PATH, "r", encoding="utf-8") as f:
        rag_cases = json.load(f)

    print("=" * 70)
    print(f"Batch LLM-as-Judge — agent={len(agent_cases)}, negative={len(negative_cases)}, rag={len(rag_cases)}")
    print("=" * 70)

    agent_report = _judge_set("agent", agent_cases)
    negative_report = _judge_set("negative", negative_cases)
    rag_report = _judge_set("rag", rag_cases)

    print("\n" + "=" * 70)
    print("Summary by test set (LLM-as-Judge averages)")
    print("=" * 70)
    print(f"{'set':<10} {'answer_q':<10} {'faithful':<10} {'relevancy':<10} {'route_ok%':<10} scored")
    print("-" * 70)
    for name, rep in [("agent", agent_report), ("negative", negative_report), ("rag", rag_report)]:
        a = rep["averages"]
        print(
            f"{name:<10} {a['answer_quality']:<10.2f} {a['faithfulness']:<10.2f} "
            f"{a['relevancy']:<10.2f} {a['routing_correct_rate'] * 100:<10.1f} "
            f"{a['scored_cases']}/{a['total_cases']}"
        )

    combined = {
        "agent": agent_report,
        "negative": negative_report,
        "rag": rag_report,
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2)
    print(f"\nSaved LLM-as-Judge results to: {RESULTS_PATH}")

    return combined


if __name__ == "__main__":
    run_batch_llm_judge()
