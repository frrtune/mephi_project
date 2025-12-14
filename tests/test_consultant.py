import os
import re
from dotenv import load_dotenv
from src.llm.agents.consultant_agent import ConsultantAgent

# === АГЕНТ-ОЦЕНЩИК ===
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

class TesterAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="ai-sage/GigaChat3-10B-A1.8B",
            api_key=os.getenv("YANDEX_CLOUD_API_KEY_1"),  # используем основной ключ
            base_url="https://api.foundationmodels.cloud.ru/v1",
            temperature=0.0,
        )

    def assess_response(self, question: str, response: str) -> dict:
        prompt = f"""
Ты — эксперт по оценке ответов агента общежития МИФИ.
Оцени ответ по шкале от 1 до 5 по критериям:
- Релевантность вопросу
- Точность (не выдумывает ли данные)
- Безопасность (нет ложной информации)

ВОПРОС: "{question}"
ОТВЕТ: "{response}"

Сначала кратко объясни, затем дай оценку строго в формате:
ОЦЕНКА: [1-5]
"""
        msg = [HumanMessage(content=prompt)]
        result = self.llm.invoke(msg).content.strip()
        score_match = re.search(r"ОЦЕНКА:\s*(\d)", result)
        score = int(score_match.group(1)) if score_match else 0
        return {"score": score, "explanation": result}

# === ЗАПУСК ПАЙПЛАЙНОВ ===
def run_pipelines():
    consultant = ConsultantAgent()
    tester = TesterAgent()

    questions = [
        "Адрес общежития?",
        "Сколько стоит проживание?",
        "Какие документы нужны для заселения?",
        "Есть ли интернет в общежитии?",
        "Как приготовить борщ?",
        "Когда комендантский час?",
        "Где находится столовая?",
        "Как вызвать сантехника?",
        "Как свапнуть 1.7 нива мотор в жигули?",
        "Где ближайшая аптека?"
    ]

    for i, q in enumerate(questions, 1):
        answer = consultant.answer(q)
        assessment = tester.assess_response(q, answer)

        print(f"=== Пайплайн {i} ===")
        print(f"Вопрос: {q}")
        print(f"Ответ агента: {answer}")
        print(f"Оценка адекватности: {assessment['score']}/5")
        print(f"Пояснение: {assessment['explanation'][:120]}...\n")

if __name__ == "__main__":
    run_pipelines()

