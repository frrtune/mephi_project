# handlers/support.py
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from handlers.sessions import save_user_turn, get_active_session  # get_active_session used? we can import from utils.session_db if needed
from utils.session_db import get_conn, get_active_session as _get_active_session

_conn = get_conn()

def support_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("Моральная поддержка", callback_data="support_morale"),
        InlineKeyboardButton("Бытовые вопросы", callback_data="support_household"),
        InlineKeyboardButton("Создать/начать сессию", callback_data="support_start_session"),
    )
    return kb

async def support_command(message: types.Message):
    await message.answer("Выберите раздел поддержки:", reply_markup=support_menu_kb())

# callback handler для выбора
async def support_callback(callback: types.CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id

    if data == "support_morale":
        # Создаём сессию автоматически, если её нет, и переводим в режим моральной поддержки
        s = _get_active_session(_conn, user_id)
        if not s:
            # импорт create_session локально чтобы не цикличить
            from utils.session_db import create_session
            sid = create_session(_conn, user_id)
            await callback.message.answer(f"Создана сессия id={sid}.")
        await callback.message.answer("💬 Вы выбрали *моральную поддержку*. Напишите, что вас беспокоит — я отвечу поддерживающе и постараюсь помочь.")
        await callback.answer()
        return

    if data == "support_household":
        s = _get_active_session(_conn, user_id)
        if not s:
            from utils.session_db import create_session
            sid = create_session(_conn, user_id)
            await callback.message.answer(f"Создана сессия id={sid}.")
        await callback.message.answer("🏠 Вы выбрали *бытовые вопросы*. Спросите про правила, оплату, процедуры и т.п.")
        await callback.answer()
        return

    if data == "support_start_session":
        from utils.session_db import create_session, get_active_session
        s = get_active_session(_conn, user_id)
        if s:
            await callback.message.answer("У вас уже есть активная сессия.")
        else:
            sid = create_session(_conn, user_id)
            await callback.message.answer(f"Сессия создана: id={sid}")
        await callback.answer()
        return

# Обработчик текстовых сообщений в режиме поддержки.
# Его нужно зарегистрировать как общий текстовый обработчик после ваших основных обработчиков.
async def handle_support_message(message: types.Message):
    """
    Если у пользователя есть активная сессия, сохраняем сообщение в неё и отвечаем.
    Примитивная логика: если сообщение содержит слова типа 'плохое', 'грустно' -> моральная поддержка.
    Вы можете заменить логику на вызов RAG/LLM.
    """
    user_id = message.from_user.id
    s = _get_active_session(_conn, user_id)
    if not s:
        # Если сессии нет — не обрабатываем здесь (пускай основной обработчик handle_text_message это делает).
        return

    # Сохраняем пользовательский ход
    save_user_turn(user_id, "user", message.text)

    txt = message.text.lower()
    # Простые эвристики
    morale_keywords = ["груст", "плохо", "депрес", "страшн", "тоска", "помоги", "зову"]
    household_keywords = ["оплат", "цена", "стоим", "документ", "заселен", "ключ", "стирал", "интернет", "прачечн", "правил"]

    if any(k in txt for k in morale_keywords):
        reply = (
            "Я слышу, что вам тяжело. Это нормально — испытывать такие чувства. "
            "Если хотите, опишите подробнее — я постараюсь поддержать и дать практические советы."
        )
        # Сохраняем ответ бота в сессии
        save_user_turn(user_id, "bot", reply)
        await message.answer(reply)
        return

    if any(k in txt for k in household_keywords):
        reply = (
            "По бытовому вопросу: обычно для заселения нужны паспорт, справка и заявление. "
            "Если уточните конкретный вопрос (оплата/кухни/интернет), дам более точный ответ."
        )
        save_user_turn(user_id, "bot", reply)
        await message.answer(reply)
        return

    # Если не понятно — эхо + подсказка
    reply = "Не совсем понял запрос. Можете уточнить: это моральная поддержка или бытовой вопрос? (Напишите несколько слов.)"
    save_user_turn(user_id, "bot", reply)
    await message.answer(reply)
