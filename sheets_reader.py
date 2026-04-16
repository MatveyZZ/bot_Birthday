# sheets_reader.py
import logging
import gspread
from datetime import datetime
import config

def get_birthdays_today():
    try:
        gc = gspread.service_account(filename='credentials.json')
        sh = gc.open_by_key(config.SHEET_ID)
        worksheet = sh.sheet1
        records = worksheet.get_all_values()
        today = datetime.now().strftime('%d.%m')
        birthday_people = []
        for row in records[1:]:  # Пропускаем заголовок
            if len(row) >= 2 and row[1] == today:
                birthday_people.append(row[0])
        return birthday_people
    except Exception as e:
        logging.error(f"Ошибка Google Sheets: {e}")
        return []