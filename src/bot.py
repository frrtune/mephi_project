"""
Основной класс бота
"""
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from utils.config import TELEGRAM_TOKEN, BOT_COMMANDS
from handlers.base import start_command, help_command, kostik_command, timurchik_valeykin_command
from handlers.messages import handle_text_message

class MifiDormBot:
    """Основной класс бота для общежития МИФИ"""
    
    def __init__(self):
        self.token = TELEGRAM_TOKEN
        if not self.token:
            raise ValueError("TELEGRAM_TOKEN не установлен!")
        
        self.bot = Bot(token=self.token)
        self.dp = Dispatcher()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        # Регистрация команд
        self.dp.message.register(start_command, Command("start"))
        self.dp.message.register(help_command, Command("help"))
        self.dp.message.register(kostik_command, Command("kostik"))
        self.dp.message.register(timurchik_valeykin_command, Command("timurchik_valeykin"))
        
        # Обработка текстовых сообщений
        self.dp.message.register(lambda msg: handle_text_message(msg, self.bot))
    
    async def set_bot_commands(self):
        """Установка команд бота"""
        commands = [
            types.BotCommand(command=cmd, description=desc)
            for cmd, desc in BOT_COMMANDS
        ]
        await self.bot.set_my_commands(commands)
    
    async def run(self):
        """Запуск бота"""
        await self.set_bot_commands()
        print("🤖 Бот запускается...")
        await self.dp.start_polling(self.bot)
