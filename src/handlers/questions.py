"""
Обработчик вопросов коменданту с RAG-агентом для общежитий МИФИ
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackContext

from llm.agents.rag_consultant_agent import RAGConsultantAgent
from utils.keyboard import get_back_button, get_questions_module_keyboard

logger = logging.getLogger(__name__)

# Глобальный экземпляр агента
rag_agent = RAGConsultantAgent()

async def handle_questions_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало работы с модулем вопросов коменданту"""
    await update.message.reply_text(
        "❓ **Вопросы коменданту**\n\n"
        "Задайте вопрос о общежитиях МИФИ:\n"
        "- Адреса и расположение\n"
        "- Стоимость проживания\n"
        "- Условия заселения\n"
        "- Правила проживания\n"
        "- Инфраструктура\n\n"
        "Я найду ответ в базе знаний общежитий МИФИ!",
        reply_markup=get_questions_module_keyboard(),
        parse_mode='Markdown'
    )

async def handle_question_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка вопроса пользователя через RAG-агента"""
    user_id = update.effective_user.id
    question = update.message.text
    
    # Показываем, что бот думает
    thinking_message = await update.message.reply_text("🔍 Ищу информацию в базе знаний МИФИ...")
    
    try:
        # Получаем ответ от RAG-агента
        result = await rag_agent.ask_question(question, user_id=str(user_id))
        
        answer = result["answer"]
        sources_count = result["sources_count"]
        
        # Формируем ответ
        response_text = f"**Ответ:** {answer}\n\n"
        
        if sources_count > 0:
            response_text += f"📚 *Найдено в базе знаний: {sources_count} источников*"
        else:
            response_text += "ℹ️ *Информация не найдена в базе знаний*"
        
        # Обновляем сообщение с ответом
        await context.bot.edit_message_text(
            chat_id=thinking_message.chat_id,
            message_id=thinking_message.message_id,
            text=response_text,
            reply_markup=get_back_button(),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка обработки вопроса: {e}")
        await context.bot.edit_message_text(
            chat_id=thinking_message.chat_id,
            message_id=thinking_message.message_id,
            text="❌ Произошла ошибка при поиске информации. Попробуйте позже.",
            reply_markup=get_back_button()
        )

async def handle_database_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ статистики базы знаний (для админов)"""
    stats = rag_agent.get_database_stats()
    
    if "error" not in stats:
        stats_text = (
            "📊 **Статистика базы знаний общежитий МИФИ:**\n\n"
            f"• Всего записей: {stats['total_records']}\n"
            f"• Категории:\n"
        )
        
        for category, count in stats['categories'].items():
            stats_text += f"  - {category}: {count} записей\n"
        
        stats_text += f"\n📍 База данных: `{stats['database_path']}`"
        
    else:
        stats_text = f"❌ Ошибка получения статистики: {stats['error']}"
    
    await update.message.reply_text(
        stats_text,
        parse_mode='Markdown',
        reply_markup=get_back_button()
    )
