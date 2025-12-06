
"""
Клиент для работы с FM API cloud.ru
"""
import asyncio
import logging
from typing import Optional
from openai import OpenAI

from utils.config import API_KEY, BASE_URL, MODEL_NAME, LLM_CONFIG

logger = logging.getLogger(__name__)

class LLMClient:
    """Клиент для работы с LLM через FM API"""
    
    def __init__(self):
        if not API_KEY:
            raise ValueError("API_KEY не установлен в конфигурации!")
        if not BASE_URL:
            raise ValueError("BASE_URL не установлен в конфигурации!")
        
        self.sdk_client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        self.model_name = MODEL_NAME
        
        # Настройки по умолчанию из конфига
        self.default_config = {
            'max_tokens': LLM_CONFIG.get('default_max_tokens', 1000),
            'temperature': LLM_CONFIG.get('default_temperature', 0.7),
            'top_p': LLM_CONFIG.get('default_top_p', 0.9),
            'timeout': LLM_CONFIG.get('timeout_seconds', 30),
            'max_retries': LLM_CONFIG.get('max_retries', 3)
        }
        
        logger.info(f"LLMClient инициализирован с моделью {MODEL_NAME}")
    
    def _validate_prompt(self, prompt: str) -> bool:
        """
        Проверка промпта перед отправкой
        
        Args:
            prompt: Текст промпта
            
        Raises:
            ValueError: Если промпт некорректен
        """
        if not prompt or len(prompt.strip()) == 0:
            raise ValueError("Промпт не может быть пустым")
        
        if len(prompt) > 10000:
            raise ValueError(f"Промпт слишком длинный ({len(prompt)} > 10000 символов)")
        
        # Проверка на потенциально опасные символы (опционально)
        dangerous_patterns = ['```', '```python', '```bash', '```shell']
        for pattern in dangerous_patterns:
            if pattern in prompt.lower():
                logger.warning(f"Промпт содержит потенциально опасный паттерн: {pattern}")
        
        return True
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Генерация ответа через FM API с retry логикой и timeout
        
        Args:
            prompt: Текст запроса
            **kwargs: Дополнительные параметры:
                - max_tokens: Максимальное количество токенов в ответе
                - temperature: Температура генерации (0.0-1.0)
                - top_p: Top-p sampling параметр
                - timeout: Таймаут запроса в секундах
                - max_retries: Максимальное количество повторных попыток
                
        Returns:
            Ответ модели
            
        Raises:
            Exception: При ошибках API или после исчерпания попыток
            ValueError: При некорректном промпте
        """
        # Валидация промпта
        self._validate_prompt(prompt)
        
        # Объединяем настройки по умолчанию с переданными параметрами
        config = {**self.default_config, **kwargs}
        
        max_retries = config.get('max_retries', 3)
        timeout = config.get('timeout', 30)
        
        logger.debug(f"Отправка запроса в LLМ (длина: {len(prompt)} chars, retries: {max_retries})")
        
        for attempt in range(max_retries):
            try:
                def sync_call_to_sdk():
                    """Синхронный вызов SDK OpenAI"""
                    return self.sdk_client.chat.completions.create(
                        model=self.model_name,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=config.get('max_tokens'),
                        temperature=config.get('temperature'),
                        top_p=config.get('top_p')
                    )
                
                # Выполняем запрос с таймаутом
                resp = await asyncio.wait_for(
                    asyncio.to_thread(sync_call_to_sdk),
                    timeout=timeout
                )
                
                response_text = resp.choices[0].message.content
                logger.debug(f"Получен ответ от LLМ (длина: {len(response_text)} chars)")
                
                # Логируем использование токенов (если доступно)
                if hasattr(resp, 'usage'):
                    usage = resp.usage
                    logger.debug(f"Использовано токенов: {usage.total_tokens} "
                               f"(prompt: {usage.prompt_tokens}, completion: {usage.completion_tokens})")
                
                return response_text
                
            except asyncio.TimeoutError:
                logger.warning(f"Таймаут запроса к FM API (попытка {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    raise Exception(f"Таймаут запроса к FM API после {max_retries} попыток")
                await asyncio.sleep(1)  # Ждем перед повторной попыткой
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Ошибка при обращении к нейросети (попытка {attempt + 1}/{max_retries}): {error_msg}")
                
                # Проверяем, является ли ошибка фатальной
                if any(fatal_error in error_msg.lower() for fatal_error in ['invalid api key', 'rate limit', 'quota exceeded']):
                    raise Exception(f"Фатальная ошибка API: {error_msg}")
                
                if attempt == max_retries - 1:
                    raise Exception(f"Ошибка при обращении к нейросети после {max_retries} попыток: {error_msg}")
                
                await asyncio.sleep(1)  # Ждем перед повторной попыткой
    
    async def generate_with_system_prompt(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        Генерация ответа с системным промптом
        
        Args:
            system_prompt: Системный промпт (инструкции для модели)
            user_prompt: Пользовательский запрос
            **kwargs: Дополнительные параметры
            
        Returns:
            Ответ модели
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        def sync_call_with_system():
            return self.sdk_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', self.default_config['max_tokens']),
                temperature=kwargs.get('temperature', self.default_config['temperature']),
                top_p=kwargs.get('top_p', self.default_config['top_p'])
            )
        
        try:
            logger.debug(f"Отправка запроса с системным промптом (система: {len(system_prompt)} chars, пользователь: {len(user_prompt)} chars)")
            
            resp = await asyncio.wait_for(
                asyncio.to_thread(sync_call_with_system),
                timeout=kwargs.get('timeout', self.default_config['timeout'])
            )
            
            return resp.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Ошибка генерации с системным промптом: {e}")
            raise

# Глобальный экземпляр клиента
llm_client = LLMClient()
