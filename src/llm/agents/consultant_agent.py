import os
# ИСПРАВЛЕНО 1: Используем ChatOpenAI
from langchain_openai import ChatOpenAI
# ИСПРАВЛЕНО 2: Импортируем из langchain_core.messages
from langchain_core.messages import HumanMessage
from src.llm.vector_store import VectorStore
import traceback


class ConsultantAgent:
    def __init__(self):
        # Инициализация с base_url для cloud.ru через ChatOpenAI
        self.llm = ChatOpenAI(
            model="ai-sage/GigaChat3-10B-A1.8B",
            api_key=os.getenv("Consultant"),
            base_url="https://foundation-models.api.cloud.ru/v1",
            temperature=0.7,
        )

        self.vector_store = VectorStore()

    def answer(self, question: str) -> str:
        # получаем контекст
        contexts = self.vector_store.similarity_search(question, k=3)

        prompt = (
            "Контекст:\n" +
            "\n".join(contexts) +
            f"\n\nВопрос: {question}\nОтвет:"
        )

        # запрос к модели
        result = self.llm.invoke([HumanMessage(content=prompt)])

        return result.content.strip()