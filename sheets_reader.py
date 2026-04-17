# sheets_reader.py (фрагмент)
import logging
import gspread
from datetime import datetime
import config

def calculate_age(birth_date_str):
    """Вычисляет возраст по дате рождения в формате ДД.ММ.ГГГГ."""
    try:
        # Удаляем возможные пробелы
        birth_date_str = birth_date_str.strip()
        # Заменяем дефисы на точки, если есть
        birth_date_str = birth_date_str.replace('-', '.')
        birth_date = datetime.strptime(birth_date_str, '%d.%m.%Y')
        today = datetime.now()
        age = today.year - birth_date.year
        # Проверяем, был ли день рождения в этом году
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        logging.info(f"   🎂 Рассчитан возраст: {age} лет (дата рождения: {birth_date_str})")
        return age
    except Exception as e:
        logging.error(f"   ❌ Ошибка при расчёте возраста для '{birth_date_str}': {e}")
        return None

def is_jubilee(age):
    """Возвращает True, если возраст юбилейный (кратен 5 или 10)."""
    return age is not None and age > 0 and (age % 5 == 0 or age % 10 == 0)

def get_birthdays_today():
    """
    Возвращает список словарей с данными именинников.
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
            if len(row) >= 3:
                full_name = row[0].strip()
                date_str = row[1].strip()
                position = row[2].strip() if len(row) > 2 else ""

                logging.info(f"📋 Строка {i}: Имя='{full_name}', Исходная дата='{date_str}', Должность='{position}'")

                if date_str:
                    # Ожидаем формат ДД.ММ.ГГГГ или ДД.ММ.ГГГГ с пробелами
                    date_str = date_str.replace('-', '.').replace(' ', '')
                    parts = date_str.split('.')
                    if len(parts) >= 3:
                        day = parts[0].zfill(2)
                        month = parts[1].zfill(2)
                        year = parts[2]
                        # Проверяем, что год 4 цифры
                        if len(year) == 4:
                            formatted_date = f"{day}.{month}"
                            logging.info(f"   ➡️ Обработанная дата: {formatted_date}.{year}")
                            if formatted_date == today:
                                # Вычисляем возраст
                                age = calculate_age(date_str)
                                is_jub = is_jubilee(age)
                                # Разделяем имя и фамилию
                                name_parts = full_name.split()
                                first_name = name_parts[0] if name_parts else full_name
                                last_name = name_parts[1] if len(name_parts) > 1 else ""
                                birthday_people.append({
                                    'full_name': full_name,
                                    'first_name': first_name,
                                    'last_name': last_name,
                                    'position': position,
                                    'age': age,
                                    'is_jubilee': is_jub
                                })
                                logging.info(f"   ✅ Найден именинник: {full_name}, возраст {age}, юбилей: {is_jub}")
                        else:
                            logging.warning(f"   ⚠️ Год не в формате 4 цифр: '{year}'")
                    else:
                        logging.warning(f"   ⚠️ Недостаточно компонентов даты: {parts}")
        return birthday_people
    except Exception as e:
        logging.error(f"❌ Ошибка Google Sheets: {e}")
        return []