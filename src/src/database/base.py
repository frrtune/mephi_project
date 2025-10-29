import os
from openai import OpenAI
api_key = os.environ["API_KEY"] = 'NjBiYzY1NmUtZjUxYi00OGE1LWJmYjMtNjRiMDgzZDYxOTNj.b0b3f4a34ce84437db9aacec1c69ac23'
url = "https://foundation-models.api.cloud.ru/v1"

client = OpenAI(
    api_key=api_key,
    base_url=url
)

\\\\\\\\\\\\\\МБ ЭТО ЛУЧШЕ(КОД СНИЗУ)?
def test_prompts(questions: list[str]):
    for question in questions:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system", 
                    "content": "Ваш системный промпт здесь"
                },
                {
                    "role": "user", 
                    "content": question
                }
            ],
            temperature=0.5,
            max_tokens=5000
        )
        print(f"Вопрос: {question}\nОтвет: {response.choices[0].message.content}\n")
///////////////////////


\\\\\\ЧЕМ ТО ЧТО НИЖЕ//////////
response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    max_tokens=5000,
    temperature=0.5,
    presence_penalty=0,
    top_p=0.95,
    messages = [
    {
        "role": "system",
        "content": (
            "Ты — дружелюбный телеграм-бот. "
            "Твой стиль общения: вежливый, но немного неформальный. "
            "Отвечай кратко, но не в ущерб информативности. "
            "Запрещено: обсуждать политику, использовать ненормативную лексику."
        )
    },
    {
        "role": "user",
        "content": "Ваш вопрос здесь"
    }
]
print(response.choices[0].message.content)


def test_prompts(test_questions):
    results = []
    for i, question in enumerate(test_questions, 1):
        print(f"Тест {i}/{len(test_questions)}: {question}")
        try:
            answer = chat_with_bot(question)
            results.append({
                "question": question,
                "answer": answer,
                "status": "success"
            })
            print(f"Ответ: {answer}\n")
        except Exception as e:
            results.append({
                "question": question, 
                "error": str(e),
                "status": "error"
            })
            print(f"Ошибка: {e}\n")
    return results



test_questions = [
    "Как приготовить пасту?",
    "Что думаешь о текущей политической ситуации?",
    "У меня болит голова, что делать?",
    "Расскажи хохму",
]
test_results = test_prompts(test_questions)

import sqlite3
import json

def init_vector_db():
    """Инициализация векторной БД в Colab"""
    conn = sqlite3.connect('bot_vector_db.sqlite')
    cursor = conn.cursor()
    
    # В Colab расширение VSS может не работать, используем обычную SQLite
    # с подготовкой для будущего добавления векторного поиска
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            embedding TEXT,  # Будем хранить векторы как JSON
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Создаем индекс для быстрого поиска
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_content ON documents(content)
    """)
    
    conn.commit()
    conn.close()
    print("Векторная БД инициализирована")

# Функция с демо-данными
def add_demo_data():
    """Демо-данные: (заполни             )"""
    pass

# Инициализируем БД при запуске
init_vector_db()
