from src.llm.agents.consultant_agent import ConsultantAgent

def test_consultant_answer():
    agent = ConsultantAgent()
    answer = agent.answer("Как пройти в библиотеку?")
    # Ожидаем, что ответ содержит этот же текст вопроса или непустой ответ
    assert "вопрос" in answer.lower() or len(answer) > 0

