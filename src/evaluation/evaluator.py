import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import anthropic

MODEL = "claude-haiku-4-5-20251001"

def evaluate_response(question: str, answer: str, agent_route: str, sources: list) -> dict:
    """Evaluates the quality of an agent response using LLM-as-Judge."""
    client = anthropic.Anthropic()

    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        system=(
            "You are an AI quality evaluator for MedNova Hospital Chennai. "
            "Evaluate the given question-answer pair on these 4 criteria. "
            "Return ONLY a JSON object with these exact keys: "
            "answer_quality (1-5), faithfulness (1-5), relevancy (1-5), routing_correct (true/false), feedback (string). "
            "answer_quality: Is the answer helpful and accurate? "
            "faithfulness: Is the answer grounded in the source data? "
            "relevancy: Does the answer address the question? "
            "routing_correct: Was the correct agent used for this question type? "
            "feedback: One sentence of constructive feedback."
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n"
                    f"Answer: {answer}\n"
                    f"Agent used: {agent_route}\n"
                    f"Sources: {sources}\n"
                    "Evaluate this response."
                )
            }
        ]
    )

    import json
    try:
        scores = json.loads(response.content[0].text)
    except json.JSONDecodeError:
        scores = {
            "answer_quality": 3,
            "faithfulness": 3,
            "relevancy": 3,
            "routing_correct": True,
            "feedback": "Could not parse evaluation response."
        }
    return scores

if __name__ == "__main__":
    scores = evaluate_response(
        question="What are the ICU visiting hours?",
        answer="ICU visiting hours are 10AM-11AM and 5PM-6PM daily.",
        agent_route="rag",
        sources=["icu_procedures.txt"]
    )
    print(scores)
