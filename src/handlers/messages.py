"""
Обработчики текстовых сообщений
"""
import asyncio
from aiogram import types
from aiogram.types import InputFile
from llm.client import llm_client

async def handle_text_message(message: types.Message, bot):
    """
    Обработка текстовых сообщений и отправка в LLM
    
    Args:
        message: Объект сообщения
        bot: Экземпляр бота для отправки действий
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

    info = await message.reply("Отправляю запрос... подожди секунду.")

    try:
        # Получаем ответ от LLM
        model_answer = await llm_client.generate_response(text)
    except Exception as e:
        await info.edit_text(f"Ошибка при обращении к нейросети: {e}")
        return

    # Если очень длинно — отправим как файл
    if len(model_answer) > 4000:
        fname = "answer.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(model_answer)
        await bot.send_document(chat_id=message.chat.id, document=InputFile(fname))
        await info.delete()
    else:
        await info.edit_text(model_answer)
