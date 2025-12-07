# benchmark.py

import time
from src.llm.agents.consultant_agent import RAGConsultantAgent

async def measure_speed():
    agent = RAGConsultantAgent()
    question = "Адрес общежития?"

    start_time = time.time()
    result = await agent.ask_question(question)
    end_time = time.time()

    speed = end_time - start_time
    print(f"Время ответа на вопрос '{question}': {speed:.2f} секунд")
    print(f"Ответ: {result['answer']}")
    print(f"Найдено источников: {result['sources_count']}")

    if speed < 3.0:
        print("✅ Скорость удовлетворительная (< 3 сек)")
    else:
        print("❌ Скорость слишком высокая (> 3 сек)")

if __name__ == "__main__":
    import asyncio
    asyncio.run(measure_speed())
