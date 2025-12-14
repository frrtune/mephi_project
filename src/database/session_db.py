import sqlite3

class SessionDB:
    def __init__(self, db_path="bot.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        # Таблица для режима (консультант/психолог)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                user_id INTEGER PRIMARY KEY,
                mode TEXT
            )
        """)
        # Таблица для истории психолога
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS psych_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message TEXT,
                response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def set_mode(self, user_id: int, mode: str):
        cursor = self.conn.cursor()
        cursor.execute("REPLACE INTO sessions (user_id, mode) VALUES (?, ?)", (user_id, mode))
        self.conn.commit()



    def get_mode(self, user_id: int) -> str:
        cursor = self.conn.cursor()
        cursor.execute("SELECT mode FROM sessions WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return row[0] if row else None

    def save_history(self, user_id: int, message: str, response: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO psych_history (user_id, message, response) VALUES (?, ?, ?)",
            (user_id, message, response)
        )
        self.conn.commit()
