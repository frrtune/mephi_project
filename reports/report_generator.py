# report_generator.py

import time
import matplotlib.pyplot as plt
from src.llm.agents.consultant_agent import RAGConsultantAgent
import asyncio

async def generate_report():
    agent = RAGConsultantAgent()
    test_questions = [
        "Адрес общежития?",
        "Сколько стоит проживание?",
        "Какие правила проживания?",
        "Какие документы нужны для заселения?",
        "Есть ли интернет в общежитии?",
        "Как приготовить борщ?",  # Нерелевантный вопрос
        "Когда комендантский час?",
        "Как вызвать сантехника?",
        "Где находится столовая?",
        "Какие категории студентов имеют приоритет?"
    ]

    results = []
    times = []

    for question in test_questions:
        start_time = time.time()
        result = await agent.ask_question(question)
        end_time = time.time()
        response_time = end_time - start_time
        times.append(response_time)

        # Простая оценка точности (можно улучшить)
        accuracy = "Высокая" if result["sources_count"] > 0 and "нет информации" not in result["answer"].lower() else "Низкая"
        if "борщ" in question.lower():
            accuracy = "Не применимо"

        results.append({
            "question": question,
            "response": result["answer"],
            "sources_count": result["sources_count"],
            "time": response_time,
            "accuracy": accuracy
        })

    # Вывод таблицы результатов
    print("\n=== ОТЧЕТ ПО КОНСУЛЬТАНТУ ===")
    print(f"{'Вопрос':<50} | {'Источники':<10} | {'Время (с)':<10} | {'Точность':<10}")
    print("-" * 90)
    for r in results:
        print(f"{r['question']:<50} | {r['sources_count']:<10} | {r['time']:<10.2f} | {r['accuracy']:<10}")

    # График времени ответа
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(test_questions)), times, tick_label=test_questions, color='skyblue')
    plt.title('Время ответа на тестовые вопросы')
    plt.ylabel('Время (сек)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    asyncio.run(generate_report())
