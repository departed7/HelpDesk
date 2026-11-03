import os
import settings

class ReportGenerator:
    @staticmethod
    def export_to_txt(data):
        filename = "tickets_report.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("ОТЧЕТ ПО ЗАЯВКАМ И БЕЗОПАСНОСТИ IT-ОТДЕЛА\n")
            f.write("=" * 55 + "\n")
            for item in data:
                f.write(f"ID: {item[0]} | Тема: {item[1]} | Статус: {item[4]}\n")
                f.write(f"Приоритет: {item[3]} | Дата: {item[5]}\n")
                f.write("-" * 55 + "\n")
            
            f.write("\nСВОДКА СИСТЕМНОГО МОНИТОРИНГА И ОШИБОК (system.log):\n")
            f.write("=" * 55 + "\n")
            if os.path.exists(settings.LOG_FILE):
                with open(settings.LOG_FILE, "r", encoding="utf-8") as log_f:
                    lines = log_f.readlines()
                    warnings = [line for line in lines if "WARNING" in line or "CRITICAL" in line or "ERROR" in line]
                    f.write(f"Всего событий в журнале: {len(lines)}\n")
                    f.write(f"Из них предупреждений и блокировок: {len(warnings)}\n\n")
                    f.write("Последние зафиксированные инциденты:\n")
                    for w in warnings[-5:]:
                        f.write(w)
            else:
                f.write("Журнал событий пуст. Ошибок не зафиксировано.\n")
                
        return filename