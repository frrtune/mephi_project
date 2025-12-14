# Ассистент коменданта общежития МИФИ

Телеграм-бот на Python 3.9+ с использованием aiogram:contentReference[oaicite:3]{index=3} и LangChain (архитектура RAG):contentReference[oaicite:4]{index=4}. 
- **Язык:** Python 3.9+  
- **Фреймворк:** aiogram  
- **LLM:** Foundation Models API от Cloud.ru (OpenAI-совместимый):contentReference[oaicite:5]{index=5}  
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
