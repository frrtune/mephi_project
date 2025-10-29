"""
Базовые обработчики команд бота
"""
from aiogram import types
from aiogram.filters import Command

async def start_command(message: types.Message):
    """Обработчик команды /start"""
    await message.answer("Привет! Я бот-комендант. Напиши свой вопрос и я отвечу.")

async def help_command(message: types.Message):
    """Обработчик команды /help"""
    await message.answer("Просто напиши сообщение — я отправлю его в нейросеть и верну ответ.")

async def kostik_command(message: types.Message):
    """Обработчик команды /kostik"""
    await message.answer("МЯУ МЯУ МЯУ Я СТУДЕНТ НИЯУ")

async def timurchik_valeykin_command(message: types.Message):
    """Обработчик команды /timurchik_valeykin"""
    await message.answer("Я ГОВОРЮ ИФТИС ВЫ ГОВОРИТЕ СИЛА!")
