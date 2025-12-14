from aiogram import Router, types
from aiogram.filters import Command
from aiogram import F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from src.database.session_db import SessionDB
from src.llm.agents.consultant_agent import ConsultantAgent
from src.llm.agents.psychologist_agent import PsychologistAgent
import logging

router = Router()
db = SessionDB()  # работа с БД сессий и истории
consultant_agent = ConsultantAgent()
psychologist_agent = PsychologistAgent()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    # Меню с кнопками
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Консультант")],
            [KeyboardButton(text="Психолог")],
        ],
        resize_keyboard=True
    )
    await message.answer("Добро пожаловать! Выберите режим работы бота:", reply_markup=keyboard)


@router.message(F.text == "Консультант")
async def start_consultant(message: types.Message):
    # Устанавливаем режим "консультант" для пользователя
    db.set_mode(message.from_user.id, 'consultant')
    await message.answer("Режим консультанта активирован. Задайте ваш вопрос.")

@router.message(F.text == "Психолог")
async def start_psychologist(message: types.Message):
    # Устанавливаем режим "психолог" для пользователя
    db.set_mode(message.from_user.id, 'psychologist')
    await message.answer("Режим психолога активирован. Расскажите, что вас беспокоит.")

@router.message(Command("kostik"))
async def start_kostik(message: types.Message):
    await message.answer("Это команда костя, которая ничего не делает. я просто её написал, потому что сижу на дискре.")



@router.message()
async def handle_all(message: types.Message):
    user_id = message.from_user.id
    mode = db.get_mode(user_id)
    text = message.text

    if mode == 'consultant':
        response = consultant_agent.answer(text)
        logging.info(f"Consultant answered for {user_id}: {response}")
        await message.answer(response)
    elif mode == 'psychologist':
        response = psychologist_agent.answer(text)
        logging.info(f"Psychologist answered for {user_id}: {response}")
        # Сохраняем историю для психолога
        db.save_history(user_id, text, response)
        await message.answer(response)
    else:
        await message.answer("Пожалуйста, сначала выберите режим работы (Консультант или Психолог).")
