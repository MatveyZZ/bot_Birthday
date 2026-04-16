# ai_generator.py
import logging
import requests
import base64
import config
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_access_token():
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    credentials = f"{config.GIGACHAT_CLIENT_ID}:{config.GIGACHAT_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "RqUID": "6f0b2e5a-7f1e-4c3d-9b2a-8e5f1a3c4d7e",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"scope": config.GIGACHAT_SCOPE}
    resp = requests.post(url, headers=headers, data=data, verify=False)
    resp.raise_for_status()
    return resp.json()["access_token"]

def generate_congratulations(name: str, position: str = "") -> str:
    try:
        token = get_access_token()
        api_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Системный промпт, максимально приближенный к стилю ваших поздравлений
        system_prompt = (
            "Ты — автор поздравлений с днём рождения для коллег в дружном рабочем чате. "
            "Твой стиль: очень тёплый, с юмором, профессиональными отсылками и обильным, но уместным использованием эмодзи. "
            "Структура поздравления:\n"
            "1. Начало: 'Добрый день, Коллеги!!!' или 'Коллеги!!!' и объявление именинника (имя, можно с отчеством если уместно). Много эмодзи.\n"
            "2. Персональное обращение к имениннику на 'ты' или 'Вы' в зависимости от должности и имени (если руководитель или с отчеством — на 'Вы', иначе на 'ты').\n"
            "3. Один-два абзаца с благодарностью, шутками и пожеланиями, связанными с должностью. Используй метафоры и юмор из профессиональной сферы.\n"
            "4. Завершение: 'Твои коллеги' или 'С уважением, Ваши коллеги' и эмодзи 🫶❤️.\n"
            "Примеры должностей и шуток:\n"
            "- Менеджер по продажам: воронка продаж, возражения клиентов, бонусы, дезинфекция сомнений.\n"
            "- Руководитель: амбициозные цели, вдохновение команды, контроль, рост бизнеса.\n"
            "- Бухгалтер: цифры сходятся, отчётность, зарплатные ведомости, проводки счастья.\n"
            "- IT-специалист: код компилируется, баги исчезают, сервера не падают, дедлайны дружелюбные.\n"
            "- HR: находить лучших, адаптация, командный дух.\n"
            "Используй эмодзи: 🎂🥳🌹💃🕺🎉👍😁🫶❤️🤗 и другие.\n"
            "Объём: 7-12 предложений."
        )

        user_prompt = f"Напиши поздравление с днём рождения для коллеги. Имя: {name}. Должность: {position if position else 'не указана'}."

        payload = {
            "model": "GigaChat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 600
        }

        resp = requests.post(api_url, headers=headers, json=payload, verify=False)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    except Exception as e:
        logging.error(f"❌ Ошибка GigaChat: {e}")
        # Запасной вариант в том же стиле
        if position:
            return f"Коллеги!!!\nСегодня день рождения у {name}! 🎂🥳\n\n{name}, с днём рождения! Желаем успехов в работе {position} и море позитива!\n\nТвои коллеги 🫶"
        else:
            return f"Коллеги!!!\nСегодня день рождения у {name}! 🎂🥳\n\n{name}, с днём рождения! Счастья, здоровья и удачи во всём!\n\nТвои коллеги 🫶"