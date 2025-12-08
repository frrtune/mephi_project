"""
Конфигурация приложения
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ---------- FM API Cloud.ru ----------
API_KEY = os.getenv('YANDEX_CLOUD_API_KEY_1', 'NjBiYzY1NmUtZjUxYi00OGE1LWJmYjMtNjRiMDgzZDYxOTNj.b0b3f4a34ce84437db9aacec1c69ac23')      # для основного агента
API_KEY_RAG = os.getenv('YANDEX_CLOUD_API_KEY_2', '')  # для RAG-агента (опционально)
BASE_URL = os.getenv('FM_API_URL', "https://foundation-models.api.cloud.ru/v1")
MODEL_NAME = os.getenv('FM_MODEL_NAME', "gpt-oss-120b")

# ---------- Настройки LLM ----------
LLM_CONFIG = {
    # Параметры по умолчанию для генерации
    'default_max_tokens': 1000,
    'default_temperature': 0.7,
    'default_top_p': 0.9,
    'timeout_seconds': 30,
    'max_retries': 3,
    
    # Настройки для разных агентов
    'consultant_agent': {
        'temperature': 0.3,
        'max_tokens': 800
    },
    'psychologist_agent': {
        'temperature': 0.8,
        'max_tokens': 600
    },
    'rag_agent': {
        'temperature': 0.2,
        'max_tokens': 1000
    }
}

# ---------- Базы данных ----------
DATABASE_CONFIG = {
    'vector_db_path': os.getenv('VECTOR_DB_PATH', 'data/mipti_dormitory_db.db'),
    'sessions_db_path': os.getenv('SESSIONS_DB_PATH', 'data/sessions.db'),
    'max_session_age_days': 7,  # Автоудаление старых сессий
    'rag_top_k': 3,  # Количество документов для RAG поиска
}

# ---------- Telegram ----------
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

# ---------- Сессии и безопасность ----------
SESSION_CONFIG = {
    'session_timeout_minutes': 30,
    'max_messages_per_session': 50,
    'enable_anonymization': True,
    'privacy_notice': "🔒 Ваши сообщения сохраняются анонимно и удаляются через 7 дней.",
    'emergency_contact': "📞 Психологическая служба МИФИ: +7 (495) 788-56-99"
}

# ---------- RAG система ----------
RAG_CONFIG = {
    'chunk_size': 500,
    'chunk_overlap': 50,
    'embedding_model': 'all-MiniLM-L6-v2',
    'similarity_threshold': 0.5,
    'max_context_length': 2000
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

# ---------- Пути к данным ----------
DATA_PATHS = {
    'knowledge_base': 'data/knowledge_base/',
    'logs': 'logs/',
    'temp_files': 'temp/'
}

# ---------- Настройки приложения ----------
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# ---------- Валидация конфигурации ----------
def validate_config():
    """Проверка обязательных настроек"""
    errors = []
    
    if not TELEGRAM_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN не установлен")
    
    if not API_KEY:
        errors.append("YANDEX_CLOUD_API_KEY_1 не установлен")
    
    # Проверка существования базы данных (опционально)
    if not os.path.exists(DATABASE_CONFIG['vector_db_path']):
        print(f"⚠️ Векторная база данных не найдена: {DATABASE_CONFIG['vector_db_path']}")
        print("   Создайте её с помощью скрипта init_database.py")
    
    # Создание необходимых папок
    for path in DATA_PATHS.values():
        os.makedirs(path, exist_ok=True)
    
    if errors:
        raise ValueError(f"Ошибки конфигурации: {', '.join(errors)}")
    
    return True

# ---------- Утилиты ----------
def get_agent_config(agent_type: str) -> dict:
    """
    Получение конфигурации для конкретного агента
    
    Args:
        agent_type: Тип агента ('consultant', 'psychologist', 'rag')
    
    Returns:
        dict: Конфигурация агента
    """
    agent_configs = {
        'consultant': LLM_CONFIG['consultant_agent'],
        'psychologist': LLM_CONFIG['psychologist_agent'],
        'rag': LLM_CONFIG.get('rag_agent', LLM_CONFIG['consultant_agent'])
    }
    
    config = agent_configs.get(agent_type, LLM_CONFIG['consultant_agent'])
    
    # Добавляем общие настройки
    config.update({
        'api_key': API_KEY_RAG if agent_type == 'rag' and API_KEY_RAG else API_KEY,
        'model_name': MODEL_NAME,
        'base_url': BASE_URL
    })
    
    return config

# Автоматическая валидация при импорте (только в production)
if ENVIRONMENT == 'production':
    try:
        validate_config()
        print("✅ Конфигурация успешно загружена")
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        raise
