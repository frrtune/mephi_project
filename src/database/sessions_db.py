"""
Сессионная база данных для агента-психолога
Простая SQLite база для хранения приватных диалогов
"""
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SessionsDB:
    """
    Простая база для хранения диалогов с психологом
    Автоматическое удаление старых записей через 7 дней
    """
    
    def __init__(self, db_path: str = "data/sessions.db"):
        """
        Инициализация сессионной базы
        
        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path
        self._init_database()
        logger.info(f"Сессионная БД инициализирована: {db_path}")
    
    def _init_database(self):
        """Создание таблиц в базе данных"""
        conn = sqlite3.connect(self.db_path)
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
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,  # 'user' или 'assistant'
                content TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        # Индексы для быстрого поиска
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON sessions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON messages(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)')
        
        conn.commit()
        conn.close()
    
    def create_session(self, user_id: int) -> str:
        """
        Создание новой сессии для пользователя
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            str: ID созданной сессии
        """
        import uuid
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO sessions (session_id, user_id, start_time, last_activity)
                VALUES (?, ?, ?, ?)
            ''', (session_id, user_id, now, now))
            
            conn.commit()
            logger.info(f"Создана новая сессия: {session_id} для user_id: {user_id}")
            
        except Exception as e:
            logger.error(f"Ошибка создания сессии: {e}")
            raise
        finally:
            conn.close()
        
        return session_id
    
    def get_active_session(self, user_id: int) -> Optional[str]:
        """
        Получение активной сессии пользователя
        Сессия активна если была активность за последние 30 минут
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            Optional[str]: ID активной сессии или None
        """
        time_limit = (datetime.now() - timedelta(minutes=30)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id FROM sessions 
            WHERE user_id = ? AND last_activity > ?
            ORDER BY last_activity DESC
            LIMIT 1
        ''', (user_id, time_limit))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def add_message(self, session_id: str, role: str, content: str):
        """
        Добавление сообщения в сессию
        
        Args:
            session_id: ID сессии
            role: 'user' или 'assistant'
            content: Текст сообщения
        """
        if not content or len(content.strip()) == 0:
            logger.warning("Попытка добавить пустое сообщение")
            return
        
        # Ограничиваем длину сообщения для БД
        if len(content) > 5000:
            content = content[:5000] + "... [обрезано]"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Добавляем сообщение
            cursor.execute('''
                INSERT INTO messages (session_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (session_id, role, content, datetime.now().isoformat()))
            
            # Обновляем время последней активности и счетчик
            cursor.execute('''
                UPDATE sessions 
                SET last_activity = ?, message_count = message_count + 1
                WHERE session_id = ?
            ''', (datetime.now().isoformat(), session_id))
            
            conn.commit()
            logger.debug(f"Сообщение добавлено в сессию {session_id}: {role}")
            
        except Exception as e:
            logger.error(f"Ошибка добавления сообщения: {e}")
            raise
        finally:
            conn.close()
    
    def get_session_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Получение истории сообщений сессии
        
        Args:
            session_id: ID сессии
            limit: Максимальное количество сообщений
            
        Returns:
            List[Dict]: История сообщений
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT role, content, timestamp 
            FROM messages 
            WHERE session_id = ? 
            ORDER BY timestamp ASC
            LIMIT ?
        ''', (session_id, limit))
        
        history = []
        for role, content, timestamp in cursor.fetchall():
            history.append({
                'role': role,
                'content': content,
                'timestamp': timestamp
            })
        
        conn.close()
        return history
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение информации о сессии
        
        Args:
            session_id: ID сессии
            
        Returns:
            Optional[Dict]: Информация о сессии
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id, user_id, start_time, last_activity, message_count
            FROM sessions 
            WHERE session_id = ?
        ''', (session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'session_id': result[0],
                'user_id': result[1],
                'start_time': result[2],
                'last_activity': result[3],
                'message_count': result[4],
                'duration_minutes': self._calculate_duration(result[2], result[3])
            }
        
        return None
    
    def _calculate_duration(self, start_time: str, last_activity: str) -> int:
        """Вычисление продолжительности сессии в минутах"""
        try:
            start = datetime.fromisoformat(start_time)
            last = datetime.fromisoformat(last_activity)
            duration = last - start
            return int(duration.total_seconds() / 60)
        except:
            return 0
    
    def cleanup_old_sessions(self, days: int = 7):
        """
        Удаление старых сессий (старше указанного количества дней)
        
        Args:
            days: Удалять сессии старше N дней
        """
        time_limit = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Находим старые сессии
            cursor.execute('''
                SELECT session_id FROM sessions 
                WHERE last_activity < ?
            ''', (time_limit,))
            
            old_sessions = [row[0] for row in cursor.fetchall()]
            
            if old_sessions:
                # Удаляем сообщения старых сессий
                placeholders = ','.join(['?' for _ in old_sessions])
                cursor.execute(f'''
                    DELETE FROM messages 
                    WHERE session_id IN ({placeholders})
                ''', old_sessions)
                
                # Удаляем сами сессии
                cursor.execute(f'''
                    DELETE FROM sessions 
                    WHERE session_id IN ({placeholders})
                ''', old_sessions)
                
                conn.commit()
                logger.info(f"Удалено {len(old_sessions)} старых сессий (старше {days} дней)")
        
        except Exception as e:
            logger.error(f"Ошибка очистки старых сессий: {e}")
        finally:
            conn.close()
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Статистика пользователя
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            Dict: Статистика пользователя
        """
        conn = sqlite3.connect(self.db_path)
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
        """Общая статистика базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM sessions')
        total_sessions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM messages')
        total_messages = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM sessions')
        unique_users = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'unique_users': unique_users,
            'database_path': self.db_path,
            'last_cleanup': datetime.now().isoformat()
        }


# Глобальный экземпляр для использования во всем приложении
sessions_db = SessionsDB()

# ==============================================
# ПРОСТОЕ ИСПОЛЬЗОВАНИЕ:
# ==============================================

if __name__ == "__main__":
    # Тестирование базы данных
    db = SessionsDB("test_sessions.db")
    
    # Создаем тестовую сессию
    user_id = 12345
    session_id = db.create_session(user_id)
    print(f"Создана сессия: {session_id}")
    
    # Добавляем сообщения
    db.add_message(session_id, "user", "Мне грустно сегодня...")
    db.add_message(session_id, "assistant", "Я понимаю, расскажите подробнее")
    
    # Получаем историю
    history = db.get_session_history(session_id)
    print(f"\nИстория сессии ({len(history)} сообщений):")
    for msg in history:
        print(f"  {msg['role']}: {msg['content'][:50]}...")
    
    # Статистика
    stats = db.get_database_stats()
    print(f"\nСтатистика БД: {stats}")
