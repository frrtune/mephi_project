from dotenv import load_dotenv
load_dotenv()
import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from src.handlers.bot_handlers import router as bot_router

TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("OPENAI_API_KEY")

# Настройка логирования
logging.basicConfig(level=logging.INFO, filename='bot.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()


# Регистрируем маршруты
dp.include_router(bot_router)

async def main():
    logging.info("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
