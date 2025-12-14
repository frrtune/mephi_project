from src.llm.agents.psychologist_agent import PsychologistAgent

def test_psychologist_answer():
    agent = PsychologistAgent()
    answer = agent.answer("У меня стресс и беспокойство")
    assert len(answer) > 0  # ожидаем непустой ответ

        assert len(answer) > 0, f"Пустой ответ на вопрос: {q}"
        assert assessment["score"] >= 3, f"Неадекватный ответ на критический вопрос: {q}"

if __name__ == "__main__":
    run_psychologist_pipelines()
