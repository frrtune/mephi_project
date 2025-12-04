"""
Конфигурация приложения
"""
import os

# ---------- Конфигурация FM API cloud.ru ----------
API_KEY = 'NjBiYzY1NmUtZjUxYi00OGE1LWJmYjMtNjRiMDgzZDYxOTNj.b0b3f4a34ce84437db9aacec1c69ac23'
BASE_URL = "https://foundation-models.api.cloud.ru/v1"
MODEL_NAME = "openai/gpt-oss-120b"

# ---------- Конфигурация Telegram Bot ----------
# Будет запрашиваться при запуске или можно установить через переменные окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')  # Если пусто - запросим при запуске

# ---------- Настройки модели ----------
MODEL_CONFIG = {
    'max_tokens': 1500,
    'temperature': 0.3,
    'top_p': 0.95
}

# ---------- Команды бота ----------
BOT_COMMANDS = [
    ("start", "Запустить бота"),
    ("help", "Помощь по боту"),
    ("stats", "Статистика базы знаний"),
    ("test_rag", "Тест RAG системы"),
    ("kostik", "Костик привет"),
    ("timurchik_valeykin", "Специальная команда Тимура"),
    ("session_start", "Начать сессионный чат"),
    ("session_status", "Статус сессии"),
    ("support", "Меню поддержки")
]

# ---------- Настройки приложения ----------
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
