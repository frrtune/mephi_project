from src.llm.agents.consultant_agent import ConsultantAgent

def test_consultant_answer():
    agent = ConsultantAgent()
    
    questions = [
        "Адрес общежития?",
        "Сколько стоит проживание?",
        "Какие документы нужны для заселения?",
        "Есть ли интернет в общежитии?",
        "Как приготовить борщ?",
        "Когда комендантский час?",
        "Где находится столовая?",
        "Как вызвать сантехника?",
        "Как?",
        "Где принимают справки о здоровье?"
    ]
    
    for q in questions:
        answer = agent.answer(q)
        print(f"Вопрос: {q}")
        print(f"Ответ: {answer}\n")
        assert "вопрос" in answer.lower() or len(answer) > 0

