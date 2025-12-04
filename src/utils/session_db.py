# utils/session_db.py
"""
Сессионная база данных для хранения контекста пользователей.
Использует sqlite3. Контекст хранится в JSON.
"""
import sqlite3
import json
import time
from typing import Optional, Dict, Any, List

DB_PATH = "mipti_dormitory_db.db"  # можно использовать ту же базу или отдельную

def get_conn(path: str = DB_PATH):
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _ensure_tables(conn)
    return conn

def _ensure_tables(conn: sqlite3.Connection):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            context TEXT DEFAULT '[]'   -- JSON array of messages/turns
        )
    ''')
    conn.commit()

def create_session(conn: sqlite3.Connection, user_id: int) -> int:
    now = int(time.time())
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sessions (user_id, active, created_at, updated_at, context) VALUES (?, 1, ?, ?, ?)",
        (user_id, now, now, json.dumps([]))
    )
    conn.commit()
    return cur.lastrowid

def get_active_session(conn: sqlite3.Connection, user_id: int) -> Optional[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM sessions WHERE user_id = ? AND active = 1 ORDER BY updated_at DESC LIMIT 1", (user_id,))
    row = cur.fetchone()
    if not row:
        return None
    return dict(row)

def update_session_context(conn: sqlite3.Connection, session_id: int, new_context: List[Dict[str, Any]]):
    now = int(time.time())
    conn.execute("UPDATE sessions SET context = ?, updated_at = ? WHERE session_id = ?",
                 (json.dumps(new_context, ensure_ascii=False), now, session_id))
    conn.commit()

def append_to_session(conn: sqlite3.Connection, session_id: int, entry: Dict[str, Any]):
    session = conn.execute("SELECT context FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
    if session is None:
        raise ValueError("Session not found")
    ctx = json.loads(session["context"] or "[]")
    ctx.append(entry)
    update_session_context(conn, session_id, ctx)

def end_session(conn: sqlite3.Connection, session_id: int):
    now = int(time.time())
    conn.execute("UPDATE sessions SET active = 0, updated_at = ? WHERE session_id = ?", (now, session_id))
    conn.commit()

def force_delete_session(conn: sqlite3.Connection, session_id: int):
    conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    conn.commit()

def clear_session_context(conn: sqlite3.Connection, session_id: int):
    update_session_context(conn, session_id, [])

def list_user_sessions(conn: sqlite3.Connection, user_id: int) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM sessions WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    rows = cur.fetchall()
    return [dict(r) for r in rows]
