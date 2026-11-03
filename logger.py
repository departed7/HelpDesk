import datetime

class SystemLogger:
    def __init__(self, filename="system.log"):
        self.filename = filename

    def log(self, message, level="INFO"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{level}] {message}\n"
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(entry)

    def get_last_logs(self, count=10):
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return f.readlines()[-count:]
        except FileNotFoundError:
            return []