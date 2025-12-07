# handlers/sessions.py
from aiogram import types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.session_db import get_conn, create_session, get_active_session, append_to_session, end_session, clear_session_context, list_user_sessions, force_delete_session

# Инициализация подключения к БД сессий (используем тот же файл)
_conn = get_conn()

# Кнопки для управления сессией
def session_controls_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(text="Завершить сессию", callback_data="end_session"),
        InlineKeyboardButton(text="Очистить контекст", callback_data="clear_context"),
    )
    kb.add(InlineKeyboardButton(text="Принудительно удалить", callback_data="delete_session"))
    return kb

async def start_session_command(message: types.Message):
    user_id = message.from_user.id
    existing = get_active_session(_conn, user_id)
    if existing:
        await message.answer("У вас уже есть активная сессия. Продолжайте или завершите её.", reply_markup=session_controls_kb())
        return

    session_id = create_session(_conn, user_id)
    await message.answer(f"✅ Сессия создана (id={session_id}). Можете задавать вопросы — я буду хранить контекст этой сессии.", reply_markup=session_controls_kb())

async def session_status_command(message: types.Message):
    user_id = message.from_user.id
    s = get_active_session(_conn, user_id)
    if s:
        await message.answer(f"🔎 Активная сессия: id={s['session_id']}, обновлена {s['updated_at']}.", reply_markup=session_controls_kb())
    else:
        await message.answer("У вас нет активной сессии. Используйте /session_start чтобы создать.")

# Коллбэки
async def session_callback_handler(callback: types.CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id
    s = get_active_session(_conn, user_id)

    if data == "end_session":
        if not s:
            await callback.message.answer("Активной сессии нет.")
        else:
            end_session(_conn, s["session_id"])
            await callback.message.answer(f"🛑 Сессия {s['session_id']} завершена.")
        await callback.answer()
        return

    if data == "clear_context":
        if not s:
            await callback.message.answer("Активной сессии нет.")
        else:
            clear_session_context(_conn, s["session_id"])
            await callback.message.answer("🧹 Контекст сессии очищен.")
        await callback.answer()
        return

    if data == "delete_session":
        if not s:
            await callback.message.answer("Активной сессии нет.")
        else:
            force_delete_session(_conn, s["session_id"])
            await callback.message.answer(f"❗ Сессия {s['session_id']} удалена принудительно.")
        await callback.answer()
        return

# Утилита — сохраняем сообщение пользователя в сессию (вызывать из общего обработчика)
def save_user_turn(user_id: int, role: str, text: str, meta: dict = None):
    s = get_active_session(_conn, user_id)
    if not s:
        return None
    entry = {
        "role": role,             # "user" / "bot" / "system"
        "text": text,
        "meta": meta or {},
        "ts": int(__import__("time").time())
    }
    append_to_session(_conn, s["session_id"], entry)
    return s["session_id"]

# Для просмотра истории сессий (опционально)
async def my_sessions_command(message: types.Message):
    user_id = message.from_user.id
    sessions = list_user_sessions(_conn, user_id)
    if not sessions:
        await message.answer("У вас нет сессий.")
        return
    lines = []
    for s in sessions[:10]:
        active = "active" if s["active"] == 1 else "closed"
        lines.append(f"id={s['session_id']} user={s['user_id']} {active} created={s['created_at']} updated={s['updated_at']}")
    await message.answer("Ваши сессии:\n" + "\n".join(lines))

async def session_callback_handler(callback: types.CallbackQuery):
    data = callback.data
    user_id = callback.from_user.id
    s = get_active_session(_conn, user_id)

    # Обработка старых callback'ов
    if data == "end_session":
        if not s:
            await callback.message.answer("У вас нет активной сессии.")
        else:
            end_session(_conn, s["session_id"])
            await callback.message.answer(f"🛑 Сессия {s['session_id']} завершена.")
        await callback.answer()
        return

    if data == "clear_context":
        if not s:
            await callback.message.answer("У вас нет активной сессии.")
        else:
            clear_session_context(_conn, s["session_id"])
            await callback.message.answer("🧹 Контекст сессии очищен.")
        await callback.answer()
        return

    if data == "delete_session":
        if not s:
            await callback.message.answer("У вас нет активной сессии.")
        else:
            force_delete_session(_conn, s["session_id"])
            await callback.message.answer(f"❗ Сессия {s['session_id']} удалена принудительно.")
        await callback.answer()
        return

    # --- НОВЫЕ CALLBACK'И ДЛЯ МОРАЛЬНОЙ ПОДДЕРЖКИ ---
    if data == "start_morale_session":
        if s:
            await callback.message.answer(
                f"У вас уже есть активная сессия (ID: {s['session_id']}). "
                f"Хотите завершить её перед началом новой? Используйте кнопку 'Завершить сессию'."
            )
        else:
            session_id = create_session(_conn, user_id)
            await callback.message.answer(
                f"🤗 Сессия моральной поддержки создана (ID: {session_id}). "
                f"Теперь вы можете делиться своими переживаниями. "
                f"Нажмите 'Завершить сессию', когда почувствуете облегчение.",
                reply_markup=session_controls_kb()
            )
        await callback.answer()
        return

    if data == "end_morale_session":
         if not s:
            await callback.message.answer("У вас нет активной сессии.")
         else:
            end_session(_conn, s["session_id"])
            await callback.message.answer(
                f"😔 Сессия моральной поддержки завершена. "
                f"Надеюсь, вам стало чуть легче. Если понадобится, я всегда рядом. /start"
            )
         await callback.answer()
         return

    # Если callback.data не совпадает ни с одним известным, можно игнорировать или логировать.
    await callback.answer("Неизвестное действие.", show_alert=True)
