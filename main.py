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

if __name__ == "__main__":
    main()
