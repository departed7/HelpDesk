import re
import settings
import database
from logger import SystemLogger

class AuthService:
    def __init__(self):
        self.db = database.DBManager()
        self.logger = SystemLogger()

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
        sql = "SELECT role FROM users WHERE login = ? AND password = ?"
        res = self.db.query(sql, (username, password))
        if res:
            self.logger.log(f"Успешный вход: {username}")
            return True, "Успешно"
        
        self.logger.log(f"Неудачная попытка входа: {username}", "WARNING")
        return False, "Неверный логин или пароль"