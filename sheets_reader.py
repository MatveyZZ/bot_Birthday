# sheets_reader.py
import logging
import gspread
from datetime import datetime
import config

def calculate_age(birth_date_str):
    try:
        birth_date = datetime.strptime(birth_date_str, '%d.%m.%Y')
        today = datetime.now()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age
    except:
        return None

def is_jubilee(age):
    return age is not None and (age % 5 == 0 or age % 10 == 0)

def get_birthdays_today():
    try:
        gc = gspread.service_account(filename='credentials.json')
        sh = gc.open_by_key(config.SHEET_ID)
        worksheet = sh.sheet1
        records = worksheet.get_all_values()
        today = datetime.now().strftime('%d.%m')
        logging.info(f"🔍 Сегодня ищем: {today}")
        birthday_people = []

        for i, row in enumerate(records[1:], start=2):
            if len(row) >= 3:
                full_name = row[0].strip()
                date_str = row[1].strip()
                position = row[2].strip() if len(row) > 2 else ""

                logging.info(f"📋 Строка {i}: Имя='{full_name}', Исходная дата='{date_str}', Должность='{position}'")

                if date_str:
                    date_str = date_str.replace('-', '.')
                    parts = date_str.split('.')
                    if len(parts) >= 3:
                        day = parts[0].zfill(2)
                        month = parts[1].zfill(2)
                        formatted_date = f"{day}.{month}"
                        if formatted_date == today:
                            age = calculate_age(date_str)
                            is_jub = is_jubilee(age)
                            birthday_people.append({
                                'full_name': full_name,
                                'position': position,
                                'age': age,
                                'is_jubilee': is_jub
                            })
                            logging.info(f"   ✅ Найден именинник: {full_name}, возраст {age}, юбилей: {is_jub}")
        return birthday_people
    except Exception as e:
        logging.error(f"❌ Ошибка Google Sheets: {e}")
        return []