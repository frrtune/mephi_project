from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from rag.retriever import retrieve_context
from agents.llm_agent import generate_response

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text
    context_text = retrieve_context(user_query)
    full_prompt = f"Контекст:\n{context_text}\n\nВопрос: {user_query}"
    answer = generate_response(full_prompt)
    await update.message.reply_text(answer)

def main():
    app = Application.builder().token("ВАШ_TELEGRAM_BOT_TOKEN").build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,  # ← обязательно импортировать
    ContextTypes,
    filters
)

from rag.retriever import retrieve_context
from agents.llm_agent import generate_response

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# === Обработка текстовых сообщений ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text
    context_text = retrieve_context(user_query)
    full_prompt = f"Контекст:\n{context_text}\n\nВопрос: {user_query}"
    answer = generate_response(full_prompt)
    
    context.user_data["last_query"] = user_query
    context.user_data["last_answer"] = answer

    keyboard = [
        [
            InlineKeyboardButton("👍 Полезно", callback_data="feedback_good"),
            InlineKeyboardButton("👎 Не полезно", callback_data="feedback_bad")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(answer, reply_markup=reply_markup)

# === Обработка нажатий на кнопки ===
async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    feedback = query.data

    # Сохраняем в файл (можно заменить на отправку в БД)
    log_entry = f"{feedback} | Query: {context.user_data.get('last_query', '')} | Answer: {context.user_data.get('last_answer', '')}\n"
    with open("feedback_log.txt", "a", encoding="utf-8") as f:
        f.write(log_entry)

    # Убираем кнопки после выбора
    await query.edit_message_reply_markup(reply_markup=None)

# === Запуск бота ===
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_feedback))  # ← РЕГИСТРАЦИЯ ХЕНДЛЕРА

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
