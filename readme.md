# Ассистент коменданта общежития МИФИ

Телеграм-бот на Python 3.9+ с использованием aiogram и LangChain (архитектура RAG):
- **Язык:** Python 3.9+  
- **Фреймворк:** aiogram  
- **LLM:** Foundation Models API от Cloud.ru (OpenAI-совместимый)
- **БД:** SQLite для хранения сессий и истории.

## Установка и запуск


1. `git clone ...`
2. Перейти в каталог проекта: `cd bot-assistant`
3. Создать виртуальное окружение и установить зависимости:  
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
