from src.llm.agents.psychologist_agent import PsychologistAgent

def test_psychologist_answer():
    agent = PsychologistAgent()
    
    questions = [
        "У меня стресс и беспокойство",
        "Я чувствую тревогу перед экзаменами",
        "Мне грустно и одиноко",
        "Я не справляюсь с учёбой",
        "Хочу покончить со всем",
        "Как справиться с прокрастинацией?",
        "Помогите, я не могу уснуть от тревоги",
        "Хочу свапнуть hemi 5.7 в волгу",
        "Просто хочется выговориться",
        "Как улучшить настроение?"
    ]
    
    for q in questions:
        answer = agent.answer(q)
        print(f"Вопрос: {q}")
        print(f"Ответ: {answer}\n")
        # Проверка: ответ не должен быть пустым
        assert len(answer) > 0, f"Пустой ответ на вопрос: {q}"

if __name__ == "__main__":
    test_psychologist_answer()
