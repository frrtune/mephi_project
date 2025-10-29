
"""
Клиент для работы с FM API cloud.ru
"""
import asyncio
from typing import Optional
from openai import OpenAI
from utils.config import API_KEY, BASE_URL, MODEL_NAME

class LLMClient:
    """Клиент для работы с LLM через FM API"""
    
    def __init__(self):
        self.sdk_client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        self.model_name = MODEL_NAME
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Генерация ответа через FM API
        
        Args:
            prompt: Текст запроса
            **kwargs: Дополнительные параметры (max_tokens, temperature, etc.)
            
        Returns:
            Ответ модели
        """
        def sync_call_to_sdk(user_text: str):
            return self.sdk_client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": user_text}],
                max_tokens=kwargs.get('max_tokens', 1500),
                temperature=kwargs.get('temperature', 0.3),
                top_p=kwargs.get('top_p', 0.95)
            )
        
        try:
            # Вызываем синхронный SDK без блокировки event loop
            resp = await asyncio.to_thread(sync_call_to_sdk, prompt)
            return resp.choices[0].message.content
        except Exception as e:
            raise Exception(f"Ошибка при обращении к нейросети: {e}")

# Глобальный экземпляр клиента
llm_client = LLMClient()
