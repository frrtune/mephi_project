import nest_asyncio
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import ChatActions

nest_asyncio.apply()

API_TOKEN = input("Введите токен бота: ")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Создаем клавиатуру для быстрого доступа
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/start"), KeyboardButton(text="/help")],
        [KeyboardButton(text="/kostik"), KeyboardButton(text="/Sergunka")],
        [KeyboardButton(text="❓ Задать вопрос")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

async def set_commands():
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Запустить бота"),
        types.BotCommand(command="help", description="Помощь по боту"),
    ])

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    # Показываем индикатор набора сообщения
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatActions.TYPING)
    await asyncio.sleep(1)

    await message.answer(
        "Привет! я твой милый помощник для житейских проблем в общежитие), если что то не понимаешь то нажимай /help",
        reply_markup=keyboard
    )

@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    # Показываем индикатор набора сообщения
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatActions.TYPING)
    await asyncio.sleep(1)

    await message.answer(
        "",
        reply_markup=keyboard
    )

@dp.message(Command("kostik"))
async def kostik_cmd(message: types.Message):
    # Показываем индикатор набора сообщения
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatActions.TYPING)
    await asyncio.sleep(2)  # Немного дольше для длинного сообщения
    await message.answer(
        "",
        reply_markup=keyboard
    )

@dp.message(Command("Sergunka"))
async def sergunka_cmd(message: types.Message):
    # Показываем индикатор набора сообщения
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatActions.TYPING)
    await asyncio.sleep(1)

    await message.answer(
        "",
        reply_markup=keyboard
    )

# Обработка кнопки "Задать вопрос"
@dp.message(lambda message: message.text == "❓ Задать вопрос")
async def ask_question_button(message: types.Message):
    # Показываем индикатор набора сообщения
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatActions.TYPING)
    await asyncio.sleep(1)

    question_examples = """
🤔 <b>Примеры вопросов, которые ты можешь задать:</b>

• <i>"Как починить Wi-Fi в общежитии?"</i>
• <i>"Где ближайшая столовая?"</i>
• <i>"Во сколько комендантский час?"</i>
• <i>"Куда обратиться с проблемой в комнате?"</i>
• <i>"Как вызвать сантехника?"</i>

Просто напиши свой вопрос в чат, и я постараюсь помочь! 💭
    """
    await message.answer(question_examples, parse_mode="HTML")

# Обработка обычных текстовых сообщений (вопросов)
@dp.message()
async def handle_questions(message: types.Message):
    # Показываем индикатор набора сообщения
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatActions.TYPING)
    await asyncio.sleep(2)  # Имитация обработки вопроса

    # Проверяем, не является ли сообщение командой
    if not message.text.startswith('/'):
        response = """
✅ <b>Ваш вопрос принят в обработку!</b>

К сожалению, я пока только учусь и не могу отвечать на произвольные вопросы.
Но вы можете:

📞 <b>Обратиться к коменданту</b> - по вопросам общежития
🔧 <b>Позвать дежурного</b> - для технических проблем
🍽️ <b>Спросить в столовой</b> - по вопросам питания

А пока воспользуйтесь доступными командами! 👇
        """
        await message.answer(response, parse_mode="HTML", reply_markup=keyboard)

# Обработка нажатий на кнопки клавиатуры
@dp.message(lambda message: message.text == "/start")
async def start_button(message: types.Message):
    await start_cmd(message)

@dp.message(lambda message: message.text == "/help")
async def help_button(message: types.Message):
    await help_cmd(message)

async def main():
    await set_commands()
    print("Бот запущен через polling...")
    await dp.start_polling(bot)

await main()
