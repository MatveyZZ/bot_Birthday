import gspread
from datetime import datetime

import config

def get_birthdays_today():
    """
    Подключается к Google Sheets и возвращает список именинников на сегодня.
    Предполагается, что в столбце A - имена, в столбце B - даты в формате 'ДД.ММ'.
    """
    try:
        # Авторизация через сервисный аккаунт
        gc = gspread.service_account(filename='credentials.json')
        sh = gc.open_by_key(config.SHEET_ID)
        worksheet = sh.sheet1

        # Получаем все данные из таблицы
        records = worksheet.get_all_values()
        # Пропускаем заголовок (если он есть) - records[1:]
        today = datetime.now().strftime('%d.%m') # Формат даты, например '08.05'

        birthday_people = []
        for row in records[1:]:  # Пропускаем первую строку (заголовок)
            if len(row) >= 2:
                name = row[0]
                date_str = row[1]
                if date_str == today:
                    birthday_people.append(name)
        
        return birthday_people

    except Exception as e:
        logging.error(f"Ошибка при чтении Google Sheets: {e}")
        return []