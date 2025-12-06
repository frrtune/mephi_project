"""
Конфигурация приложения
"""
pip install python-dotenv
import os
from dotenv import load_dotenv

load_dotenv()

# ---------- FM API Cloud.ru ----------
API_KEY = os.getenv('YANDEX_CLOUD_API_KEY_1')      # для основного агента
API_KEY_RAG = os.getenv('YANDEX_CLOUD_API_KEY_2')  # для RAG-агента
BASE_URL = "https://foundation-models.api.cloud.ru/v1" 
MODEL_NAME = "openai/gpt-oss-120b"

# ---------- Настройки генерации ----------
MODEL_CONFIG = {
    'max_tokens': 1500,
    'temperature': 0.3,
    'top_p': 0.95
}

RAG_AGENT_CONFIG = {
    'max_tokens': 1500,
    'temperature': 0.2,  
    'top_p': 0.9
}

# ---------- Telegram ----------
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

# ---------- Команды и прочее ----------
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

DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
