!pip install openai aiogram nest_asyncio httpx --quiet

import os
import asyncio
import nest_asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

nest_asyncio.apply()

# ---------- Конфигурация ----------
# TELEGRAM_TOKEN: токен бота из BotFather
# API_KEY: ключ для foundation-models.api.cloud.ru (или положи в переменную окружения API_KEY)
TELEGRAM_TOKEN = input('Введите TELEGRAM_TOKEN: ').strip()
API_KEY = 'NjBiYzY1NmUtZjUxYi00OGE1LWJmYjMtNjRiMDgzZDYxOTNj.b0b3f4a34ce84437db9aacec1c69ac23'
BASE_URL = "https://foundation-models.api.cloud.ru/v1"

# ---------- Инициализация SDK (синхронного) ----------
# Мы используем синхронный SDK OpenAI, поэтому будем вызывать его в to_thread
from openai import OpenAI
sdk_client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# модель — как у тебя в примере
MODEL_NAME = "openai/gpt-oss-120b"

# ---------- Telegram bot ----------
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

async def set_commands():
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Запустить бота"),
        types.BotCommand(command="help", description="Помощь по боту"),
        types.BotCommand(command="kostik", description="Костик привет"),
        types.BotCommand(command="timurchik_valeykin", description="Специальная команда Тимура")
    ])

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Привет! Я бот-комендант. Напиши свой вопрос и я отвечу.")
@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer("Просто напиши сообщение — я отправлю его в нейросеть и верну ответ.")
@dp.message(Command("kostik"))
async def help_cmd(message: types.Message):
    await message.answer("МЯУ МЯУ МЯУ Я СТУДЕНТ НИЯУ")
@dp.message(Command("timurchik_valeykin"))
async def help_cmd(message: types.Message):
    await message.answer("Я ГОВОРЮ ИФТИС ВЫ ГОВОРИТЕ СИЛА!")

# любой текстовый message -> отправляем в SDK и возвращаем ответ
@dp.message()
async def forward_to_model(message: types.Message):
    text = (message.text or "").strip()
    if not text:
        await message.reply("Пустое сообщение — отправь, пожалуйста, вопрос текстом.")
        return

    # покажем пользователю, что бот 'печатает'
    try:
        await bot.send_chat_action(chat_id=message.chat.id, action=types.ChatActions.TYPING)
    except Exception:
        pass

    info = await message.reply("Отправляю запрос... подожди секунду.")

    # функция, которую выполним в стороннем потоке (синхронный SDK)
    def sync_call_to_sdk(user_text: str):
        return sdk_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": user_text}],
            max_tokens=1500,     # подправь при необходимости
            temperature=0.3,
            top_p=0.95
        )

    try:
        # вызываем синхронный SDK без блокировки event loop
        resp = await asyncio.to_thread(sync_call_to_sdk, text)
    except Exception as e:
        await info.edit_text(f"Ошибка при обращении к нейросети: {e}")
        return

    # пытаемся достать текст ответа (формат SDK: resp.choices[0].message.content)
    try:
        model_answer = resp.choices[0].message.content
    except Exception:
        # на случай, если структура другая — просто приведём к строке
        model_answer = str(resp)

    # если очень длинно — отправим как файл
    if len(model_answer) > 4000:
        fname = "answer.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(model_answer)
        await bot.send_document(chat_id=message.chat.id, document=open(fname, "rb"))
        await info.delete()
    else:
        await info.edit_text(model_answer)

async def main():
    await set_commands()
    print("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

