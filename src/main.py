"""
Точка входа в приложение - Telegram бот для общежитий МИФИ
Запускает бота с двумя агентами: консультант и психолог
"""
import asyncio
import logging
import os

# Правильные импорты из текущего пакета
from .bot import MifiDormBot
from .utils.config import TELEGRAM_TOKEN, DEBUG, LOG_LEVEL, validate_config
from .database import init_database

# Настройка логирования
def setup_logging():
    """Настройка системы логирования"""
    log_level = getattr(logging, LOG_LEVEL.upper())
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(),  # В консоль
            logging.FileHandler('logs/bot.log', encoding='utf-8')  # В файл
        ]
    )
    
    # Создаем папку для логов если её нет
    os.makedirs('logs', exist_ok=True)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Логирование настроено (уровень: {LOG_LEVEL})")
    
    return logger

async def startup():
    """Действия при запуске приложения"""
    print("\n" + "="*50)
    print("🏠 ЗАПУСК БОТА ДЛЯ ОБЩЕЖИТИЙ МИФИ")
    print("="*50)
    
    logger = logging.getLogger(__name__)
    
    # Проверяем конфигурацию
    try:
        validate_config()
        logger.info("✅ Конфигурация проверена")
    except ValueError as e:
        logger.error(f"❌ Ошибка конфигурации: {e}")
        print(f"\n💡 Решение: Создайте файл .env в корне проекта")
        print("   И добавьте TELEGRAM_BOT_TOKEN=ваш_токен")
        return False
    
    # Проверяем наличие токена
    if not TELEGRAM_TOKEN:
        print("\n🔑 Токен Telegram бота не найден!")
        print("1. Получите токен у @BotFather")
        print("2. Добавьте в файл .env:")
        print("   TELEGRAM_BOT_TOKEN=ваш_токен_здесь")
        print("\nИли введите токен сейчас:")
        token = input("TELEGRAM_TOKEN: ").strip()
        
        if not token:
            logger.error("Токен не предоставлен. Завершение работы.")
            return False
        
        # Временно устанавливаем токен
        from .utils import config
        config.TELEGRAM_TOKEN = token
        logger.info("Токен установлен через ввод")
    
    # Инициализируем базы данных
    logger.info("Инициализация баз данных...")
    db_success = init_database()
    
    if not db_success:
        logger.warning("Базы данных не инициализированы, но продолжаем...")
    
    return True

async def shutdown():
    """Действия при завершении работы"""
    logger = logging.getLogger(__name__)
    logger.info("Завершение работы бота...")
    
    print("\n👋 Бот завершил работу")

async def main():
    """Основная функция запуска"""
    # Настраиваем логирование
    logger = setup_logging()
    
    try:
        # Выполняем действия при запуске
        can_start = await startup()
        if not can_start:
            print("\n❌ Не удалось запустить бота")
            return
        
        # Создаем и запускаем бота
        print("\n🤖 Создание экземпляра бота...")
        bot = MifiDormBot()
        
        print("\n🚀 Запуск бота...")
        print("   Для остановки нажмите Ctrl+C")
        print("-" * 30)
        
        await bot.run()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Остановка по запросу пользователя")
        logger.info("Бот остановлен пользователем")
    except ValueError as e:
        print(f"\n❌ Ошибка: {e}")
        logger.error(f"Ошибка запуска: {e}")
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        logger.exception(f"Критическая ошибка: {e}")
    finally:
        await shutdown()

if __name__ == "__main__":
    # Создаем папку для данных если её нет
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Запускаем приложение
    asyncio.run(main())
