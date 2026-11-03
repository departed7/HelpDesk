import sqlite3
import hashlib
import settings
from logger import SystemLogger

class DBManager:
    def __init__(self):
        self.logger = SystemLogger()
        self.conn = sqlite3.connect(settings.DB_NAME)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT UNIQUE,
                password TEXT,
                role TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT,
                status TEXT DEFAULT 'Новая',
                created_at TEXT
            )
        ''')
        admin_hash = hashlib.sha256(settings.ADMIN_PASS.encode("utf-8")).hexdigest()
        self.cursor.execute("SELECT COUNT(*) FROM users")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("INSERT INTO users (login, password, role) VALUES (?, ?, ?)", 
                               (settings.ADMIN_LOGIN, admin_hash, 'admin'))
        else:
            self.cursor.execute("UPDATE users SET password = ? WHERE login = ?", 
                               (admin_hash, settings.ADMIN_LOGIN))
        self.conn.commit()

    def query(self, sql, params=(), commit=False):
        try:
            self.cursor.execute(sql, params)
            if commit:
                self.conn.commit()
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.log(f"SQL Error: {e}", "ERROR")
            return []