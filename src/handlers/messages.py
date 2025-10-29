"""
Обработчики текстовых сообщений с RAG
"""
import asyncio
from aiogram import types
from aiogram.types import InputFile

# Импортируем RAG агента
from llm.agents.rag_consultant_agent import RAGConsultantAgent

# Создаем экземпляр RAG агента
rag_agent = RAGConsultantAgent()

async def handle_text_message(message: types.Message, bot):
    """
    Обработка текстовых сообщений с использованием RAG
    """
    text = (message.text or "").strip()
    if not text:
        await message.reply("Пустое сообщение — отправь, пожалуйста, вопрос текстом.")
        return

    # Покажем пользователю, что бот 'печатает'
    try:
        await bot.send_chat_action(chat_id=message.chat.id, action=types.ChatActions.TYPING)
    except Exception:
        pass

    info = await message.reply("🔍 Ищу информацию в базе знаний общежитий МИФИ...")

    try:
        # Используем RAG агента вместо прямого вызова нейросети
        result = await rag_agent.ask_question(
            question=text, 
            user_id=str(message.from_user.id),
            limit=3
        )
        
        answer = result["answer"]
        sources_count = result["sources_count"]
        
        # Добавляем информацию об источниках
        if sources_count > 0:
            response_text = f"**Ответ:** {answer}\n\n📚 *Найдено в базе знаний: {sources_count} источников*"
        else:
            response_text = f"**Ответ:** {answer}\n\nℹ️ *Информация не найдена в базе знаний*"
        
        await info.edit_text(response_text, parse_mode='Markdown')
        
    except Exception as e:
        await info.edit_text(f"❌ Ошибка при поиске информации: {e}")
