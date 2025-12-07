"""
Основной класс бота
"""
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from handlers.sessions import start_session_command, session_status_command, session_callback_handler, my_sessions_command
from handlers.support import support_command, support_callback, handle_support_message
from utils.session_db import get_conn  
from handlers.base import (
    start_command,
    help_command,
    kostik_command,
    timurchik_valeykin_command,
    database_stats_command,
    test_rag_command,
    morale_support_command
)
from handlers.messages import handle_text_message, handle_session_message_aiogram



from utils.config import TELEGRAM_TOKEN, BOT_COMMANDS
from handlers.base import (
    start_command, 
    help_command, 
    kostik_command, 
    timurchik_valeykin_command,
    database_stats_command,
    test_rag_command
)
from handlers.messages import handle_text_message

class MifiDormBot:
    """Основной класс бота для общежития МИФИ"""
    def _setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        # Регистрация команд
        self.dp.message.register(start_command, Command("start"))
        self.dp.message.register(help_command, Command("help"))
        self.dp.message.register(kostik_command, Command("kostik"))
        self.dp.message.register(timurchik_valeykin_command, Command("timurchik_valeykin"))
        self.dp.message.register(database_stats_command, Command("stats"))
        self.dp.message.register(test_rag_command, Command("test_rag"))
        self.dp.message.register(morale_support_command, Command("morale_support"))
        self.dp.message.register(start_session_command, Command("session_start"))
        self.dp.message.register(session_status_command, Command("session_status"))
        self.dp.message.register(my_sessions_command, Command("my_sessions"))
        self.dp.message.register(lambda msg: handle_session_message_aiogram(msg, self.bot))
        self.dp.message.register(lambda msg: handle_text_message(msg, self.bot))

        self.dp.callback_query.register(session_callback_handler)
    def __init__(self):
        self.token = TELEGRAM_TOKEN
        if not self.token:
            
            self.token = input('Введите TELEGRAM_TOKEN: ').strip()
            self.session_conn = get_conn() 
            
        if not self.token:
            raise ValueError("TELEGRAM_TOKEN не установлен!")
        
        self.bot = Bot(token=self.token)
        self.dp = Dispatcher()
        self._setup_handlers()
        self._setup_error_handlers()
    
    def _setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        
        self.dp.message.register(start_command, Command("start"))
        self.dp.message.register(help_command, Command("help"))
        self.dp.message.register(kostik_command, Command("kostik"))
        self.dp.message.register(timurchik_valeykin_command, Command("timurchik_valeykin"))
        self.dp.message.register(database_stats_command, Command("stats"))
        self.dp.message.register(test_rag_command, Command("test_rag"))
        self.dp.message.register(start_session_command, Command("session_start"))
        self.dp.message.register(session_status_command, Command("session_status"))
        self.dp.message.register(my_sessions_command, Command("my_sessions"))

        self.dp.message.register(support_command, Command("support"))

        self.dp.message.register(handle_support_message) 
        
        self.dp.callback_query.register(session_callback_handler)
        self.dp.callback_query.register(support_callback)

        

        self.dp.message.register(lambda msg: handle_text_message(msg, self.bot))
        
    
    def _setup_error_handlers(self):
        """Настройка обработчиков ошибок"""
        @self.dp.errors()
        async def error_handler(event, exception):
            """Глобальный обработчик ошибок"""
            print(f"❌ Ошибка в боте: {exception}")
            # Можно добавить отправку уведомления админу или в логи
    
    async def set_bot_commands(self):
        """Установка команд бота"""
        try:
            commands = [
                types.BotCommand(command=cmd, description=desc)
                for cmd, desc in BOT_COMMANDS
            ]
            await self.bot.set_my_commands(commands)
            print("✅ Команды бота установлены")
        except Exception as e:
            print(f"❌ Ошибка установки команд: {e}")
    
    async def on_startup(self):
        """Действия при запуске бота"""
        print("🎉 Бот успешно запущен!")
        print("📚 База знаний: общежития МИФИ")
        print("🤖 Ожидание сообщений...")
        
        # Проверяем доступность базы данных
        try:
            from handlers.base import rag_agent
            stats = rag_agent.get_database_stats()
            if "error" not in stats:
                print(f"📊 База данных: {stats['total_records']} записей")
            else:
                print(f"⚠️ Предупреждение: {stats['error']}")
        except Exception as e:
            print(f"⚠️ Не удалось проверить базу данных: {e}")
    
    async def on_shutdown(self):
        """Действия при остановке бота"""
        print("🛑 Остановка бота...")
        # Можно добавить закрытие соединений с БД и т.д.
    
    async def run(self):
        """Запуск бота"""
        try:
            await self.set_bot_commands()
            await self.on_startup()
            print("🤖 Бот запускается...")
            await self.dp.start_polling(self.bot)
        except Exception as e:
            print(f"❌ Критическая ошибка при запуске: {e}")
        finally:
            await self.on_shutdown()
