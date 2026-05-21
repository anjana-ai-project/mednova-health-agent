import sys
import json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import context_precision, context_recall
# from ragas.metrics import faithfulness, answer_relevancy  # Requires OpenAI key — uncomment when OpenAI key is available

from src.rag_engine.retriever import retrieve
from src.agents.rag_agent import rag_agent

TEST_SET_PATH = Path(__file__).resolve().parent / "test_data" / "rag_test_set.json"
RESULTS_PATH = Path(__file__).resolve().parent / "results" / "ragas_results.json"


def run_ragas_evaluation() -> dict:
    with open(TEST_SET_PATH, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    questions: list = []
    answers: list = []
    contexts_list: list = []
    ground_truths: list = []
    sources_list: list = []

    print(f"Running RAGAS evaluation on {len(test_cases)} RAG test cases...\n")
    for i, case in enumerate(test_cases, start=1):
        q = case["question"]
        print(f"  [{i}/{len(test_cases)}] {q}")
        chunks = retrieve(q)
        contexts = [c["chunk"] for c in chunks]
        sources = sorted({c["source"] for c in chunks})
        result = rag_agent(q)
        answer = result["answer"]

        questions.append(q)
        answers.append(answer)
        contexts_list.append(contexts)
        ground_truths.append(case["reference_answer"])
        sources_list.append(sources)

    ds = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts_list,
        "ground_truth": ground_truths,
    })

    print("\nScoring with [context_precision, context_recall]...")
    result = evaluate(ds, metrics=[context_precision, context_recall])

    df = result.to_pandas()

    per_question = []
    for i, row in df.iterrows():
        case = test_cases[i]
        entry = {
            "question": case["question"],
            "expected_source": case["expected_source"],
            "retrieved_sources": sources_list[i],
            "context_precision": float(row.get("context_precision", 0.0) or 0.0),
            "context_recall": float(row.get("context_recall", 0.0) or 0.0),
        }
        per_question.append(entry)

    averages = {
        "context_precision": float(df["context_precision"].mean()) if "context_precision" in df.columns else 0.0,
        "context_recall": float(df["context_recall"].mean()) if "context_recall" in df.columns else 0.0,
    }

    print("\nPer-question scores:")
    print(f"{'#':<3} {'precision':<10} {'recall':<10} {'source match':<14} question")
    for i, entry in enumerate(per_question, start=1):
        source_match = entry["expected_source"] in entry["retrieved_sources"]
        print(
            f"{i:<3} {entry['context_precision']:<10.3f} {entry['context_recall']:<10.3f} "
            f"{str(source_match):<14} {entry['question']}"
        )

    print("\nAverages:")
    for k, v in averages.items():
        print(f"  {k}: {v:.3f}")

    report = {
        "metric_set": ["context_precision", "context_recall"],
        "num_test_cases": len(test_cases),
        "averages": averages,
        "per_question": per_question,
    }

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nSaved RAGAS results to: {RESULTS_PATH}")

    return report


if __name__ == "__main__":
    run_ragas_evaluation()
