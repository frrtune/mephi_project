import json
from agents.llm_agent import generate_response
from rag.retriever import retrieve_context

def evaluate():
    with open("evaluation/dataset.json", "r", encoding="utf-8") as f:
        cases = json.load(f)

    correct = 0
    total = len(cases)

    for case in cases:
        context = retrieve_context(case["question"])
        prompt = f"Контекст:\n{context}\n\nВопрос: {case['question']}"
        actual = generate_response(prompt).strip().lower()
        expected = case["expected_answer"].strip().lower()

        # Простая проверка по подстроке
        if expected in actual or any(w in actual for w in expected.split()[:3]):
            correct += 1

    print(f"Accuracy (rough): {correct}/{total} = {correct/total:.2%}")

if __name__ == "__main__":
    evaluate()
