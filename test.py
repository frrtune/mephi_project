import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Гарантируем загрузку
load_dotenv()

try:
    llm = ChatOpenAI(
        model="ai-sage/GigaChat3-10B-A1.8B",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://foundation-models.api.cloud.ru/v1",
        temperature=0.7,
    )

    # Попробуйте простой вызов
    print("Отправка запроса...")
    result = llm.invoke([HumanMessage(content="Привет! Кто ты?")])

    print("--- Ответ получен ---")
    print(result.content)

except Exception as e:
    print(f"❌ Ошибка LLM: {e}")