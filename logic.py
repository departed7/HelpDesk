import datetime
import os
import re
import settings
import database
from logger import SystemLogger

class TicketService:
    def __init__(self):
        self.db = database.DBManager()
        self.logger = SystemLogger()

    def check_security_threats(self, text):
        threats = ["DROP", "SELECT", "DELETE", "UPDATE", "INSERT", "--", ";", "<SCRIPT>"]
        for word in threats:
            if word in text.upper():
                self.logger.log(f"Блокировка SQL-инъекции: {text}", "CRITICAL")
                return False
        return True

    def create_ticket(self, title, description, priority):
        if not self.check_security_threats(title) or not self.check_security_threats(description):
            return False, "Сработала защита (ПК 4.4): Обнаружены запрещенные символы или попытка инъекции кода!"

        if not re.search('[a-zA-Zа-яА-Я]', title) or len(title.strip()) < 4:
            return False, "Ошибка валидации: Тема должна содержать осмысленный текст (минимум 4 буквы), а не только цифры."
        
        if len(description.strip()) < 10:
            return False, "Ошибка валидации: Подробно опишите проблему (минимум 10 символов)."

        now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        sql = "INSERT INTO tickets (title, description, priority, status, created_at) VALUES (?, ?, ?, ?, ?)"
        self.db.query(sql, (title.strip(), description.strip(), priority, "Новая", now), commit=True)
        self.logger.log(f"Создана заявка: {title}")
        return True, "Успешно"

    def update_status(self, t_id, new_status):
        self.db.query("UPDATE tickets SET status = ? WHERE id = ?", (new_status, t_id), commit=True)
        self.logger.log(f"Статус заявки {t_id} изменен на {new_status}")

    def remove_ticket(self, t_id):
        self.db.query("DELETE FROM tickets WHERE id = ?", (t_id,), commit=True)
        self.logger.log(f"Удалена заявка ID: {t_id}", "WARNING")

    def get_list(self, filter_text=""):
        if not self.check_security_threats(filter_text):
            return []
        if filter_text:
            sql = "SELECT * FROM tickets WHERE title LIKE ? OR status LIKE ? OR CAST(id AS TEXT) LIKE ?"
            p = f'%{filter_text}%'
            return self.db.query(sql, (p, p, p))
        return self.db.query("SELECT * FROM tickets ORDER BY id DESC")

    def get_system_stats(self):
        try:
            db_size = os.path.getsize(settings.DB_NAME) / 1024 if os.path.exists(settings.DB_NAME) else 0
            tickets = self.db.query("SELECT COUNT(*) FROM tickets")[0][0]
            err_count = 0
            if os.path.exists(settings.LOG_FILE):
                with open(settings.LOG_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                    err_count = content.count("ERROR") + content.count("CRITICAL") + content.count("WARNING")
            return {
                "db_size": f"{db_size:.2f} KB",
                "total_tickets": tickets,
                "status": "Стабильно",
                "errors": f"Предупреждений: {err_count}" if err_count > 0 else "Ошибок нет"
            }
        except:
            return {"db_size": "0 KB", "total_tickets": 0, "status": "Ошибка", "errors": "Ошибка доступа"}