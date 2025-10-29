"""
Точка входа приложения
"""
import asyncio
import nest_asyncio
from bot import MifiDormBot

# Применяем nest_asyncio для Jupyter окружения
nest_asyncio.apply()

async def main():
    """Основная функция запуска"""
    try:
        bot = MifiDormBot()
        await bot.run()
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        print("💡 Убедитесь, что TELEGRAM_TOKEN установлен в config.py")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
