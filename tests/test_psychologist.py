from src.llm.agents.psychologist_agent import PsychologistAgent

def test_psychologist_answer():
    agent = PsychologistAgent()
    answer = agent.answer("У меня стресс и беспокойство")
    assert len(answer) > 0  # ожидаем непустой ответ

