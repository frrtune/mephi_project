import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import logging  # Добавляем для логирования оценки

# Импорт TesterAgent из локального файла
from src.llm.agents.tester_agent import TesterAgent
from src.llm.vector_store import VectorStore

# Настройка базового логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Загружаем переменные окружения
load_dotenv()


# --- АГЕНТ ---

class PsychologistAgent:
    """
    Агент-психолог с RAG и функцией самоконтроля.
    Теперь метод answer возвращает ТОЛЬКО строку-ответ.
    """

    def __init__(self):

        # Используем конфигурацию с Cloud.ru, как в вашем исходном коде
        # Примечание: Убедитесь, что проблема с ошибкой 403 решена (VPN/ключ).
        self.llm = ChatOpenAI(
            model="ai-sage/GigaChat3-10B-A1.8B",
            api_key=os.getenv("Psychologist"),
            base_url="https://foundation-models.api.cloud.ru/v1",
            temperature=0.8,
        )

        self.vector_store = VectorStore()
        self.tester = TesterAgent()

        self.system_message = SystemMessage(
            content=(
                "Ты — опытный и эмпатичный психолог. Отвечай мягко, поддерживающе и конструктивно. "
                "Используй предоставленный ниже контекст как основу для своего ответа."
            )
        )

    # ИЗМЕНЕНИЕ: Теперь возвращаем str, как в ConsultantAgent
    def answer(self, question: str) -> str:
        """
        Использует RAG для генерации ответа психолога, оценивает его,
        и возвращает только сгенерированный текст.
        """

        # 1. ПОЛУЧЕНИЕ КОНТЕКСТА (Retrieval)
        contexts = self.vector_store.similarity_search(question, k=3)
        context_str = "\n".join(contexts)

        # 2. ФОРМИРОВАНИЕ ПРОМПТА И ГЕНЕРАЦИЯ ОТВЕТА
        full_prompt = (
                "Контекст для ответа:\n" +
                "---------------------\n" +
                context_str +
                "\n---------------------\n" +
                f"\nВопрос пользователя: {question}\n\nОтвет психолога:"
        )

        messages = [
            self.system_message,
            HumanMessage(content=full_prompt)
        ]

        psychologist_response = self.llm.invoke(messages).content.strip()

        # 3. АВТОМАТИЧЕСКАЯ ОЦЕНКА ТЕСТЕРОМ (ОЦЕНКА ОСТАЕТСЯ, НО НЕ ВОЗВРАЩАЕТСЯ)
        try:
            assessment_result = self.tester.assess_response(question, psychologist_response)
            score = assessment_result.get("score")

            # Логируем результат для контроля качества, не отправляя его пользователю
            logging.info(f"Оценка ответа: {score}/5. Вопрос: {question[:50]}...")

            if score is not None and score < 3:
                logging.warning(f"Низкая оценка качества ({score}) для вопроса: {question}")

        except Exception as e:
            # Логируем ошибку, если тестирование не удалось, но продолжаем работать
            logging.error(f"Ошибка при оценке ответа: {e}")

        # 4. ВОЗВРАТ РЕЗУЛЬТАТА (ТОЛЬКО ОТВЕТ)
        return psychologist_response
