"""
Базовые обработчики команд бота
"""
from aiogram import types
from aiogram.filters import Command
from llm.agents.rag_consultant_agent import RAGConsultantAgent
from utils.keyboard import get_morale_support_keyboard
from utils.session_db import get_active_session, create_session, get_conn
# Создаем экземпляр RAG агента
rag_agent = RAGConsultantAgent()

async def start_command(message: types.Message):
    """Обработчик команды /start"""
    welcome_text = """
🏠 *Привет! Я бот-помощник коменданта общежитий МИФИ*

Я могу помочь вам с информацией об общежитиях:

📍 *Адреса и расположение*
💰 *Стоимость проживания* 
📋 *Правила проживания*
📄 *Документы для заселения*
🏢 *Инфраструктура и удобства*

Просто задайте вопрос о общежитиях МИФИ, и я найду ответ в базе знаний!

*Доступные команды:*
/help - Помощь по боту
/stats - Статистика базы знаний
/kostik - Специальная команда
    """
    await message.answer(welcome_text, parse_mode='Markdown')

async def help_command(message: types.Message):
    """Обработчик команды /help"""
    help_text = """
🤖 *Помощь по боту-коменданту*

*Как работает бот:*
1. Вы задаете вопрос о общежитиях МИФИ
2. Я ищу информацию в базе знаний
3. Отвечаю на основе официальных данных

*Примеры вопросов:*
• "Какие адреса общежитий МИФИ?"
• "Сколько стоит проживание?"
• "Какие документы нужны для заселения?"
• "Есть ли интернет в общежитиях?"

*Команды:*
/start - Начать работу
/stats - Статистика базы знаний
/kostik - Веселая команда
/timurchik_valeykin - Специальная команда

*Если информации нет в базе* - рекомендую обратиться к коменданту лично!
    """
    await message.answer(help_text, parse_mode='Markdown')

async def kostik_command(message: types.Message):
    """Обработчик команды /kostik"""
    await message.answer("МЯУ МЯУ МЯУ Я СТУДЕНТ НИЯУ 🐱")

async def timurchik_valeykin_command(message: types.Message):
    """Обработчик команды /timurchik_valeykin"""
    await message.answer("Я ГОВОРЮ ИФТИС ВЫ ГОВОРИТЕ СИЛА! 💪")

async def database_stats_command(message: types.Message):
    """Обработчик команды /stats - статистика базы знаний"""
    try:
        stats = rag_agent.get_database_stats()
        
        if "error" not in stats:
            stats_text = """
📊 *Статистика базы знаний общежитий МИФИ*

*Общая информация:*
• Всего записей: {total_records}
• Категории в базе:
{categories}

*Путь к базе:* `{db_path}`
            """.format(
                total_records=stats["total_records"],
                categories="\n".join([f"  - {cat}: {count} зап." for cat, count in stats["categories"].items()]),
                db_path=stats["database_path"]
            )
        else:
            stats_text = f"❌ *Ошибка получения статистики:* {stats['error']}"
        
        await message.answer(stats_text, parse_mode='Markdown')
        
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении статистики: {e}")

async def test_rag_command(message: types.Message):
    """Тестовая команда для проверки RAG (можно удалить после тестирования)"""
    test_question = "Какие адреса общежитий МИФИ?"
    
    try:
        result = await rag_agent.ask_question(
            question=test_question,
            user_id=str(message.from_user.id),
            limit=3
        )
        
        response = f"""
🧪 *Тест RAG системы*

*Вопрос:* {test_question}
*Ответ:* {result['answer']}
*Найдено источников:* {result['sources_count']}
*Использован контекст:* {'✅ Да' if result['context_used'] else '❌ Нет'}
        """
        
        await message.answer(response, parse_mode='Markdown')
        
    except Exception as e:
        await message.answer(f"❌ Ошибка тестирования RAG: {e}")

async def morale_support_command(message: types.Message):
    """Обработчик команды /morale_support"""
    welcome_text = """
🤗 *Режим моральной поддержки*

Здесь вы можете поделиться своими переживаниями, стрессами или трудностями.
Ваши сообщения будут сохраняться в сессию, чтобы я мог лучше понимать контекст.

Нажмите кнопку "Начать сессию", если хотите начать (или перезапустить), или "Завершить сессию", когда почувствуете облегчение.
    """

    user_id = message.from_user.id
    active_session = get_active_session(get_conn(), user_id)

    if not active_session:
        session_id = create_session(get_conn(), user_id)
        status_text = f"\n\n✅ *Новая сессия создана (ID: {session_id})*"
    else:
        status_text = f"\n\nℹ️ *Активная сессия (ID: {active_session['session_id']})*"

    await message.answer(
        welcome_text + status_text,
        parse_mode='Markdown',
        reply_markup=get_morale_support_keyboard()
    )
