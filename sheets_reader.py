# sheets_reader.py
import logging
import gspread
from datetime import datetime
import config

def get_birthdays_today():
    """
    Возвращает список кортежей (имя, должность) для именинников.
    """
    try:
        gc = gspread.service_account(filename='credentials.json')
        sh = gc.open_by_key(config.SHEET_ID)
        worksheet = sh.sheet1
        records = worksheet.get_all_values()
        today = datetime.now().strftime('%d.%m')
        logging.info(f"🔍 Сегодня ищем: {today}")
        birthday_people = []

        for i, row in enumerate(records[1:], start=2):
            if len(row) >= 2:
                name = row[0].strip()
                date_str = row[1].strip()
                position = row[2].strip() if len(row) > 2 else ""

                logging.info(f"📋 Строка {i}: Имя='{name}', Исходная дата='{date_str}', Должность='{position}'")

                if date_str:
                    date_str = date_str.replace('-', '.')
                    parts = date_str.split('.')
                    if len(parts) >= 2:
                        day = parts[0].zfill(2)
                        month = parts[1].zfill(2)
                        formatted_date = f"{day}.{month}"
                        logging.info(f"   ➡️ Обработанная дата: {formatted_date}")
                        if formatted_date == today:
                            birthday_people.append((name, position))
                            logging.info(f"   ✅ Найден именинник: {name} ({position})")
        return birthday_people
    except Exception as e:
        logging.error(f"❌ Ошибка Google Sheets: {e}")
        return []