import hashlib
import re
import settings
import database
from logger import SystemLogger

class AuthService:
    def __init__(self):
        self.db = database.DBManager()
        self.logger = SystemLogger()

    @staticmethod
    def get_sha256(text):
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def check_file_integrity(filepath="main.py"):
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(block)
        return sha256_hash.hexdigest()[:16]

    def validate_password_policy(self, password):
        if len(password) < 6:
            return False, "Пароль должен содержать минимум 6 символов"
        if not re.search(r"[A-ZА-Я]", password):
            return False, "Пароль должен содержать хотя бы одну заглавную букву"
        if not re.search(r"\d", password):
            return False, "Пароль должен содержать хотя бы одну цифру"
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Пароль должен содержать спецсимвол (!, @, #, $ и т.д.)"
        return True, ""

    def authenticate(self, username, password):
        pwd_hash = self.get_sha256(password)
        sql = "SELECT role FROM users WHERE login = ? AND password = ?"
        res = self.db.query(sql, (username, pwd_hash))
        if res:
            self.logger.log(f"Успешный вход (SHA-256): {username}")
            return True, "Успешно"
        
        self.logger.log(f"Неудачная попытка входа: {username}", "WARNING")
        return False, "Неверный логин или пароль"