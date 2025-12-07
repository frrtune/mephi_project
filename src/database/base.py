"""
Базовая SQLite база данных для проекта МИФИ
Простая реализация без сложных зависимостей
"""
import sqlite3
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from database.models import MIFIKnowledgeBase, KnowledgeItem, Session, Message, UserStats

logger = logging.getLogger(__name__)

class MIFIDatabase:
    """
    Основная база данных проекта МИФИ
    Объединяет векторную базу знаний и сессионную базу
    """
    
    def __init__(self, knowledge_db_path: str = "data/mifi_knowledge.db", 
                 sessions_db_path: str = "data/sessions.db"):
        """
        Инициализация базы данных
        
        Args:
            knowledge_db_path: Путь к базе знаний
            sessions_db_path: Путь к сессионной базе
        """
        self.knowledge_db_path = knowledge_db_path
        self.sessions_db_path = sessions_db_path
        
        # Инициализируем обе базы
        self._init_knowledge_database()
        self._init_sessions_database()
        
        # Заполняем базу знаний данными из models.py
        self._populate_knowledge_base()
        
        logger.info(f"База данных МИФИ инициализирована")
        logger.info(f"  База знаний: {knowledge_db_path}")
        logger.info(f"  Сессионная база: {sessions_db_path}")
    
    def _init_knowledge_database(self):
        """Инициализация базы знаний"""
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        
        # Таблица знаний
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY,
                text TEXT NOT NULL,
                category TEXT NOT NULL,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Индекс для поиска по категории
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON knowledge(category)')
        
        conn.commit()
        conn.close()
    
    def _init_sessions_database(self):
        """Инициализация сессионной базы"""
        conn = sqlite3.connect(self.sessions_db_path)
        cursor = conn.cursor()
        
        # Таблица сессий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                start_time TIMESTAMP NOT NULL,
                last_activity TIMESTAMP NOT NULL,
                message_count INTEGER DEFAULT 0
            )
        ''')
        
        # Таблица сообщений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        # Индексы
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_session_id ON session_messages(session_id)')
        
        conn.commit()
        conn.close()
    
    def _populate_knowledge_base(self):
        """Заполнение базы знаний данными из models.py"""
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже данные
        cursor.execute('SELECT COUNT(*) FROM knowledge')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Берем данные из MIFIKnowledgeBase
            knowledge_items = MIFIKnowledgeBase.get_all_knowledge()
            
            for i, item in enumerate(knowledge_items, 1):
                cursor.execute('''
                    INSERT INTO knowledge (id, text, category, tags)
                    VALUES (?, ?, ?, ?)
                ''', (i, item.text, item.category, ','.join(item.tags)))
            
            conn.commit()
            logger.info(f"База знаний заполнена: {len(knowledge_items)} записей")
        else:
            logger.info(f"База знаний уже содержит {count} записей")
        
        conn.close()
    
    # ==============================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С БАЗОЙ ЗНАНИЙ
    # ==============================================
    
    def search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Поиск в базе знаний по ключевым словам
        
        Args:
            query: Поисковый запрос
            limit: Максимальное количество результатов
            
        Returns:
            List[Dict]: Найденные записи
        """
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        
        # Разбиваем запрос на слова
        query_words = query.lower().split()
        
        # Ищем все записи
        cursor.execute('SELECT text, category, tags FROM knowledge')
        all_records = cursor.fetchall()
        conn.close()
        
        # Простой алгоритм релевантности
        results = []
        for text, category, tags_str in all_records:
            text_lower = text.lower()
            relevance = 0
            
            # Считаем совпадения слов
            for word in query_words:
                if len(word) > 2 and word in text_lower:
                    relevance += 1
            
            # Также проверяем теги
            if tags_str:
                tags = tags_str.lower().split(',')
                for word in query_words:
                    if len(word) > 2 and word in tags:
                        relevance += 2  # Совпадение в тегах важнее
            
            if relevance > 0:
                results.append({
                    'text': text,
                    'category': category,
                    'tags': tags_str.split(',') if tags_str else [],
                    'relevance': relevance
                })
        
        # Сортируем по релевантности
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        return results[:limit]
    
    def get_knowledge_by_category(self, category: str) -> List[str]:
        """
        Получить все записи из категории
        
        Args:
            category: Категория для поиска
            
        Returns:
            List[str]: Тексты записей
        """
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT text FROM knowledge 
            WHERE category = ?
            ORDER BY id
        ''', (category,))
        
        results = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def add_knowledge(self, text: str, category: str, tags: str = ""):
        """
        Добавить новую запись в базу знаний
        
        Args:
            text: Текст записи
            category: Категория
            tags: Ключевые слова через запятую
        """
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        
        # Находим максимальный ID
        cursor.execute('SELECT MAX(id) FROM knowledge')
        max_id = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            INSERT INTO knowledge (id, text, category, tags)
            VALUES (?, ?, ?, ?)
        ''', (max_id + 1, text, category, tags))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Добавлена новая запись: {category} - {text[:50]}...")
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Статистика базы знаний"""
        conn = sqlite3.connect(self.knowledge_db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM knowledge')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT category) FROM knowledge')
        categories_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT category, COUNT(*) FROM knowledge GROUP BY category')
        by_category = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total_records': total,
            'categories_count': categories_count,
            'by_category': by_category,
            'database_path': self.knowledge_db_path
        }
    
    # ==============================================
    # МЕТОДЫ ДЛЯ РАБОТЫ С СЕССИЯМИ
    # ==============================================
    
    def create_session(self, user_id: int) -> str:
        """
        Создать новую сессию
        
        Args:
            user_id: ID пользователя
            
        Returns:
            str: ID созданной сессии
        """
        import uuid
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.sessions_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (session_id, user_id, start_time, last_activity)
            VALUES (?, ?, ?, ?)
        ''', (session_id, user_id, now, now))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Создана сессия {session_id} для user_id: {user_id}")
        return session_id
    
    def get_active_session(self, user_id: int, timeout_minutes: int = 30) -> Optional[str]:
        """
        Получить активную сессию пользователя
        
        Args:
            user_id: ID пользователя
            timeout_minutes: Таймаут неактивности в минутах
            
        Returns:
            Optional[str]: ID активной сессии или None
        """
        # Вычисляем время таймаута
        from datetime import datetime, timedelta
        timeout_time = (datetime.now() - timedelta(minutes=timeout_minutes)).isoformat()
        
        conn = sqlite3.connect(self.sessions_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id FROM sessions 
            WHERE user_id = ? AND last_activity > ?
            ORDER BY last_activity DESC
            LIMIT 1
        ''', (user_id, timeout_time))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def add_session_message(self, session_id: str, role: str, content: str):
        """
        Добавить сообщение в сессию
        
        Args:
            session_id: ID сессии
            role: 'user' или 'assistant'
            content: Текст сообщения
        """
        # Ограничиваем длину для базы данных
        if len(content) > 5000:
            content = content[:5000] + "... [обрезано]"
        
        conn = sqlite3.connect(self.sessions_db_path)
        cursor = conn.cursor()
        
        # Добавляем сообщение
        cursor.execute('''
            INSERT INTO session_messages (session_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (session_id, role, content, datetime.now().isoformat()))
        
        # Обновляем время последней активности и счетчик
        cursor.execute('''
            UPDATE sessions 
            SET last_activity = ?, message_count = message_count + 1
            WHERE session_id = ?
        ''', (datetime.now().isoformat(), session_id))
        
        conn.commit()
        conn.close()
    
    def get_session_messages(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Получить историю сообщений сессии
        
        Args:
            session_id: ID сессии
            limit: Максимальное количество сообщений
            
        Returns:
            List[Dict]: История сообщений
        """
        conn = sqlite3.connect(self.sessions_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT role, content, timestamp 
            FROM session_messages 
            WHERE session_id = ? 
            ORDER BY timestamp ASC
            LIMIT ?
        ''', (session_id, limit))
        
        messages = []
        for role, content, timestamp in cursor.fetchall():
            messages.append({
                'role': role,
                'content': content,
                'timestamp': timestamp,
                'is_user': role == 'user',
                'is_assistant': role == 'assistant'
            })
        
        conn.close()
        return messages
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о сессии
        
        Args:
            session_id: ID сессии
            
        Returns:
            Optional[Dict]: Информация о сессии
        """
        conn = sqlite3.connect(self.sessions_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id, user_id, start_time, last_activity, message_count
            FROM sessions 
            WHERE session_id = ?
        ''', (session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Вычисляем продолжительность
            start = datetime.fromisoformat(result[2])
            last = datetime.fromisoformat(result[3])
            duration = last - start
            
            return {
                'session_id': result[0],
                'user_id': result[1],
                'start_time': result[2],
                'last_activity': result[3],
                'message_count': result[4],
                'duration_minutes': int(duration.total_seconds() / 60)
            }
        
        return None
    
    def cleanup_old_sessions(self, days: int = 7):
        """
        Удалить старые сессии
        
        Args:
            days: Удалить сессии старше N дней
        """
        time_limit = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.sessions_db_path)
        cursor = conn.cursor()
        
        # Находим старые сессии
        cursor.execute('SELECT session_id FROM sessions WHERE last_activity < ?', (time_limit,))
        old_sessions = [row[0] for row in cursor.fetchall()]
        
        if old_sessions:
            # Удаляем сообщения старых сессий
            placeholders = ','.join(['?' for _ in old_sessions])
            cursor.execute(f'DELETE FROM session_messages WHERE session_id IN ({placeholders})', old_sessions)
            
            # Удаляем сами сессии
            cursor.execute(f'DELETE FROM sessions WHERE session_id IN ({placeholders})', old_sessions)
            
            conn.commit()
            logger.info(f"Удалено {len(old_sessions)} старых сессий (старше {days} дней)")
        
        conn.close()
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Получить статистику пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict: Статистика пользователя
        """
        conn = sqlite3.connect(self.sessions_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_sessions,
                SUM(message_count) as total_messages,
                MAX(last_activity) as last_session
            FROM sessions 
            WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'user_id': user_id,
            'total_sessions': result[0] or 0,
            'total_messages': result[1] or 0,
            'last_session': result[2] or 'никогда',
            'has_active_session': self.get_active_session(user_id) is not None
        }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Общая статистика всех баз данных"""
        knowledge_stats = self.get_knowledge_stats()
        
        conn = sqlite3.connect(self.sessions_db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM sessions')
        total_sessions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM session_messages')
        total_messages = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM sessions')
        unique_users = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'knowledge_base': knowledge_stats,
            'sessions': {
                'total_sessions': total_sessions,
                'total_messages': total_messages,
                'unique_users': unique_users,
                'database_path': self.sessions_db_path
            },
            'last_cleanup': datetime.now().isoformat()
        }


# ==============================================
# ГЛОБАЛЬНЫЙ ЭКЗЕМПЛЯР ДЛЯ ИСПОЛЬЗОВАНИЯ
# ==============================================

# Создаем глобальный экземпляр базы данных
mifi_database = MIFIDatabase()

# ==============================================
# ФУНКЦИИ ДЛЯ ОБРАТНОЙ СОВМЕСТИМОСТИ
# ==============================================

def create_database():
    """Создать базу данных (для обратной совместимости)"""
    return mifi_database

def search_data(query: str, limit: int = 5):
    """Поиск в базе знаний (для обратной совместимости)"""
    results = mifi_database.search_knowledge(query, limit)
    
    # Форматируем в старый формат если нужно
    formatted = []
    for r in results:
        formatted.append((
            0,  # ID
            r['text'],
            r['category'],
            ','.join(r['tags']),
            0.8  # similarity score
        ))
    
    return formatted

def add_preloaded_data():
    """Добавить предзагруженные данные (уже сделано в конструкторе)"""
    pass

# ==============================================
# ТЕСТИРОВАНИЕ
# ==============================================

if __name__ == "__main__":
    print("🧪 Тестирование базы данных МИФИ")
    print("=" * 50)
    
    db = MIFIDatabase("test_knowledge.db", "test_sessions.db")
    
    # Тест базы знаний
    print("\n📚 Тест базы знаний:")
    stats = db.get_knowledge_stats()
    print(f"Всего записей: {stats['total_records']}")
    
    # Тест поиска
    results = db.search_knowledge("адрес общежития", limit=3)
    print(f"\n🔍 Поиск 'адрес общежития': {len(results)} результатов")
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r['text'][:50]}... (релевантность: {r['relevance']})")
    
    # Тест сессий
    print("\n💬 Тест сессий:")
    user_id = 12345
    session_id = db.create_session(user_id)
    print(f"Создана сессия: {session_id}")
    
    # Добавляем сообщения
    db.add_session_message(session_id, "user", "Привет!")
    db.add_session_message(session_id, "assistant", "Привет! Как дела?")
    
    # Получаем историю
    messages = db.get_session_messages(session_id)
    print(f"Сообщений в сессии: {len(messages)}")
    
    # Статистика
    print("\n📊 Общая статистика:")
    full_stats = db.get_database_stats()
    print(f"База знаний: {full_stats['knowledge_base']['total_records']} записей")
    print(f"Сессий: {full_stats['sessions']['total_sessions']}")
    print(f"Сообщений: {full_stats['sessions']['total_messages']}")
    
    # Очистка тестовых файлов
    import os
    if os.path.exists("test_knowledge.db"):
        os.remove("test_knowledge.db")
    if os.path.exists("test_sessions.db"):
        os.remove("test_sessions.db")
    
    print("\n✅ Все тесты пройдены!")
