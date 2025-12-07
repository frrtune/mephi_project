"""
Агент-Психолог для эмоциональной поддержки студентов МИФИ
Использует сессионную базу данных для конфиденциальности
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from llm.client import llm_client
from llm.prompts.psychologist_prompts import (
    get_psychologist_prompt_with_history,
    get_crisis_intervention_prompt,
    detect_crisis_keywords,
    get_welcome_message,
    get_privacy_notice,
    format_history
)
from database.sessions_db import sessions_db

logger = logging.getLogger(__name__)

class PsychologistAgent:
    """
    Агент для моральной поддержки студентов МИФИ
    Сохраняет историю диалогов с автоочисткой
    """
    
    def __init__(self):
        self.name = "Психолог"
        self.max_history_messages = 10  # Сколько сообщений помнить для контекста
        
        # Автоматическая очистка старых сессий при инициализации
        sessions_db.cleanup_old_sessions(days=7)
        logger.info(f"Агент-психолог инициализирован. Максимальная история: {self.max_history_messages} сообщений")
    
    async def chat(self, user_id: int, user_message: str) -> Dict[str, Any]:
        """
        Основной метод общения с агентом-психологом
        
        Args:
            user_id: ID пользователя в Telegram
            user_message: Сообщение пользователя
            
        Returns:
            Dict с ответом и метаданными
        """
        try:
            # Проверка на кризисные ситуации
            if detect_crisis_keywords(user_message):
                logger.warning(f"Обнаружены кризисные ключевые слова от user_id: {user_id}")
                return await self._handle_crisis_situation(user_id, user_message)
            
            # Получаем или создаем сессию
            session_id = await self._get_or_create_session(user_id)
            
            # Получаем историю диалога
            history = sessions_db.get_session_history(session_id, limit=self.max_history_messages)
            
            # Форматируем историю для промпта
            formatted_history = format_history(history)
            
            # Формируем промпт с историей
            prompt = get_psychologist_prompt_with_history(user_message, formatted_history)
            
            # Генерируем ответ
            response = await llm_client.generate_response(
                prompt,
                temperature=0.8,  # Более эмпатичные, креативные ответы
                max_tokens=600    # Эмоциональные ответы могут быть длиннее
            )
            
            # Сохраняем оба сообщения в базу
            sessions_db.add_message(session_id, "user", user_message)
            sessions_db.add_message(session_id, "assistant", response)
            
            # Получаем информацию о сессии для статистики
            session_info = sessions_db.get_session_info(session_id)
            
            return {
                "response": response,
                "session_id": session_id,
                "message_count": session_info["message_count"] if session_info else 0,
                "is_new_session": len(history) == 0,
                "has_crisis": False
            }
            
        except Exception as e:
            logger.error(f"Ошибка в агенте-психологе: {e}")
            # Fallback ответ
            return {
                "response": "Извините, произошла ошибка. Пожалуйста, попробуйте позже или обратитесь в психологическую службу МИФИ: +7 (495) 788-56-99",
                "session_id": None,
                "message_count": 0,
                "is_new_session": False,
                "has_crisis": False,
                "error": str(e)
            }
    
    async def _get_or_create_session(self, user_id: int) -> str:
        """
        Получение активной сессии или создание новой
        
        Args:
            user_id: ID пользователя
            
        Returns:
            str: ID сессии
        """
        # Пытаемся найти активную сессию (последние 30 минут)
        session_id = sessions_db.get_active_session(user_id)
        
        if not session_id:
            # Создаем новую сессию
            session_id = sessions_db.create_session(user_id)
            logger.info(f"Создана новая сессия для user_id: {user_id}, session_id: {session_id}")
        else:
            logger.debug(f"Найдена активная сессия: {session_id} для user_id: {user_id}")
        
        return session_id
    
    async def _handle_crisis_situation(self, user_id: int, user_message: str) -> Dict[str, Any]:
        """
        Обработка кризисных ситуаций
        
        Args:
            user_id: ID пользователя
            user_message: Кризисное сообщение
            
        Returns:
            Dict с экстренным ответом
        """
        try:
            # Формируем кризисный промпт
            prompt = get_crisis_intervention_prompt(user_message)
            
            # Генерируем экстренный ответ
            response = await llm_client.generate_response(
                prompt,
                temperature=0.3,  # Более детерминированный ответ
                max_tokens=400,
                timeout=10  # Быстрый ответ важен
            )
            
            # Создаем сессию для кризисного диалога
            session_id = sessions_db.create_session(user_id)
            
            # Сохраняем кризисный диалог
            sessions_db.add_message(session_id, "user", "[КРИЗИСНОЕ СООБЩЕНИЕ] " + user_message)
            sessions_db.add_message(session_id, "assistant", response)
            
            # Логируем кризисную ситуацию
            logger.critical(f"КРИЗИСНАЯ СИТУАЦИЯ: user_id={user_id}, session_id={session_id}")
            
            return {
                "response": response,
                "session_id": session_id,
                "message_count": 2,
                "is_new_session": True,
                "has_crisis": True,
                "emergency_contacts_shown": True
            }
            
        except Exception as e:
            logger.error(f"Ошибка обработки кризисной ситуации: {e}")
            # Fallback кризисный ответ
            return {
                "response": """
🚨 **ЭКСТРЕННАЯ ПОМОЩЬ**

Если вам нужна срочная помощь:
1. Позвоните в психологическую службу МИФИ: +7 (495) 788-56-99
2. Телефон доверия: 8-800-2000-122 (круглосуточно, бесплатно)
3. Экстренная психологическая помощь: 051 (с мобильного)

Вы не одни, помощь доступна 24/7!""",
                "session_id": None,
                "message_count": 0,
                "is_new_session": False,
                "has_crisis": True,
                "emergency_contacts_shown": True
            }
    
    def start_new_session(self, user_id: int) -> Dict[str, Any]:
        """
        Принудительное начало новой сессии
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict с информацией о новой сессии
        """
        session_id = sessions_db.create_session(user_id)
        
        return {
            "session_id": session_id,
            "welcome_message": get_welcome_message(),
            "privacy_notice": get_privacy_notice(),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_session_status(self, user_id: int) -> Dict[str, Any]:
        """
        Получение статуса текущей сессии
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict с информацией о сессии
        """
        session_id = sessions_db.get_active_session(user_id)
        
        if not session_id:
            return {
                "has_active_session": False,
                "message": "Активная сессия не найдена. Начните новый диалог."
            }
        
        session_info = sessions_db.get_session_info(session_id)
        user_stats = sessions_db.get_user_stats(user_id)
        
        if session_info:
            return {
                "has_active_session": True,
                "session_id": session_id,
                "start_time": session_info["start_time"],
                "last_activity": session_info["last_activity"],
                "message_count": session_info["message_count"],
                "duration_minutes": session_info["duration_minutes"],
                "total_user_sessions": user_stats["total_sessions"],
                "total_user_messages": user_stats["total_messages"]
            }
        
        return {
            "has_active_session": False,
            "message": "Информация о сессии не найдена."
        }
    
    def end_session(self, user_id: int) -> bool:
        """
        Завершение текущей сессии (очистка из активных)
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: Успешность завершения
        """
        # В нашей простой реализации сессии завершаются автоматически по таймауту
        # Но можно добавить флаг 'is_active' в будущем
        logger.info(f"Запрос на завершение сессии для user_id: {user_id}")
        return True
    
    async def evaluate_conversation_quality(self, session_id: str) -> Dict[str, Any]:
        """
        Оценка качества диалога (для тестирования)
        
        Args:
            session_id: ID сессии
            
        Returns:
            Dict с оценкой качества
        """
        try:
            history = sessions_db.get_session_history(session_id, limit=20)
            
            if len(history) < 3:
                return {
                    "session_id": session_id,
                    "message_count": len(history),
                    "quality_score": 0,
                    "evaluation": "Недостаточно данных для оценки"
                }
            
            # Формируем промпт для оценки
            conversation_text = "\n".join([f"{msg['role']}: {msg['content'][:100]}" for msg in history])
            
            evaluation_prompt = f"""
            Оцени качество диалога психологической поддержки:

            ДИАЛОГ:
            {conversation_text}

            Оцени по шкале 1-10:
            1. Эмпатия и понимание
            2. Безопасность рекомендаций
            3. Полезность для пользователя
            4. Соблюдение профессиональных границ

            Верни оценку в формате:
            Эмпатия: X/10
            Безопасность: X/10
            Полезность: X/10
            Границы: X/10
            Итог: X/10
            """
            
            evaluation = await llm_client.generate_response(
                evaluation_prompt,
                temperature=0.3,
                max_tokens=300
            )
            
            # Парсим оценку (простая реализация)
            lines = evaluation.split('\n')
            scores = {}
            
            for line in lines:
                if '/' in line:
                    parts = line.split(':')
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip().split('/')[0]
                        if value.isdigit():
                            scores[key] = int(value)
            
            total_score = sum(scores.values()) / len(scores) if scores else 0
            
            return {
                "session_id": session_id,
                "message_count": len(history),
                "quality_score": round(total_score, 1),
                "scores": scores,
                "evaluation_text": evaluation,
                "is_crisis_detected": any("[КРИЗИС" in msg['content'] for msg in history)
            }
            
        except Exception as e:
            logger.error(f"Ошибка оценки качества: {e}")
            return {
                "session_id": session_id,
                "error": str(e),
                "quality_score": 0
            }


# Глобальный экземпляр для использования
psychologist_agent = PsychologistAgent()

# ==============================================
# ПРОСТОЕ ИСПОЛЬЗОВАНИЕ:
# ==============================================

async def test_psychologist_agent():
    """Тестирование агента-психолога"""
    agent = PsychologistAgent()
    
    # Тест 1: Нормальный диалог
    print("🧪 Тест 1: Нормальный диалог")
    result1 = await agent.chat(99999, "Сегодня тяжелый день, устал от учебы")
    print(f"Ответ: {result1['response'][:100]}...")
    print(f"Новая сессия: {result1['is_new_session']}")
    print(f"Сообщений: {result1['message_count']}")
    
    # Тест 2: Продолжение диалога
    print("\n🧪 Тест 2: Продолжение диалога")
    result2 = await agent.chat(99999, "Не знаю, как справиться с нагрузкой")
    print(f"Ответ: {result2['response'][:100]}...")
    print(f"Новая сессия: {result2['is_new_session']}")
    
    # Тест 3: Статус сессии
    print("\n🧪 Тест 3: Статус сессии")
    status = agent.get_session_status(99999)
    print(f"Активная сессия: {status.get('has_active_session', False)}")
    if status.get('has_active_session'):
        print(f"Сообщений в сессии: {status.get('message_count', 0)}")

if __name__ == "__main__":
    asyncio.run(test_psychologist_agent())
