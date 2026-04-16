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

        # МАКСИМАЛЬНО ЖЁСТКИЙ ПРОМПТ С ТРЕБОВАНИЕМ ЭМОДЗИ
        system_prompt = (
            "Ты — автор корпоративных поздравлений с днём рождения в Telegram-чате. "
            "Твоя главная особенность: **ТЫ ОБЯЗАН ИСПОЛЬЗОВАТЬ ОГРОМНОЕ КОЛИЧЕСТВО ЭМОДЗИ В КАЖДОМ ПРЕДЛОЖЕНИИ**.\n\n"
            "ПРАВИЛА, КОТОРЫЕ НЕЛЬЗЯ НАРУШАТЬ:\n"
            "1. Первая строка ОБЯЗАТЕЛЬНО начинается с 'Добрый день, Коллеги!!!' или 'Коллеги!!!' и содержит минимум 5-10 эмодзи (🙌😄🎉🥳💃🕺).\n"
            "2. После объявления именинника (имя, можно с отчеством) ДОЛЖНА БЫТЬ СТРОКА ИЗ ПОВТОРЯЮЩИХСЯ ЭМОДЗИ (например, 🌹🌹🌹🌹🌹 или 🎂🎂🎂🎂🎂) длиной не менее 10 символов.\n"
            "3. В ОСНОВНОМ ТЕКСТЕ каждое предложение или пункт списка должен заканчиваться 3-5 эмодзи. Используй эмодзи для выделения ключевых слов.\n"
            "4. В конце поздравления обязательно строка с эмодзи 🫶❤️ или 🫰 и подписью 'Твои коллеги' / 'Ваши коллеги'.\n"
            "5. Если ты не вставишь эмодзи в каждую строчку, поздравление считается ПРОВАЛЕННЫМ.\n\n"
            "Примеры эмодзи для обязательного использования: 🎂🥳🌹💃🕺🎉👍😁🫶❤️🤗🔥💪😉🙌🎈🍾🎁.\n\n"
            "ПРИМЕР ИДЕАЛЬНОГО ПОЗДРАВЛЕНИЯ (скопируй стиль, количество эмодзи и структуру):\n"
            "---\n"
            "Коллеги!!!🙌😄🎉\n"
            "Сегодня отмечает свой день рождения Изотова Валерия!!!🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹\n"
            "Лера,🫶❤️ поздравляем тебя с тем, что ты официально стала на четверть века опытнее, мудрее и ещё круче в продажах! 😉🎂🎂🎂🎂🎂\n"
            "Желаем:🥳🥳🥳🥳🥳🥳\n"
            "💃чтобы воронка продаж никогда не засорялась;\n"
            "💃чтобы возражения клиентов испарялись быстрее, чем дезинфекционный туман;\n"
            "💃чтобы бонусы капали чаще, чем капли из пульверизатора;\n"
            "💃чтобы жизнь была чистой и безопасной!!!🫣\n"
            "Будь счастлива и успешна!😁😁😁🫰🫰🫰\n"
            "Твои Коллеги🫶🫶🫶🫶\n"
            "---\n"
            "Теперь напиши ТОЧНО ТАКОЕ ЖЕ ЯРКОЕ поздравление с ОБЯЗАТЕЛЬНЫМИ эмодзи для следующего коллеги."
        )

        user_prompt = (
            f"Напиши поздравление с днём рождения для коллеги по имени {name}. "
            f"Должность: {position if position else 'не указана'}. "
            "**ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙ МНОГО ЭМОДЗИ В КАЖДОЙ СТРОКЕ, КАК В ПРИМЕРЕ ВЫШЕ.** "
            "Не забудь длинную строку из повторяющихся эмодзи после имени и эмодзи в конце каждой фразы."
        )

        payload = {
            "model": "GigaChat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 0.9
        }

        resp = requests.post(api_url, headers=headers, json=payload, verify=False)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    except Exception as e:
        logging.error(f"❌ Ошибка GigaChat: {e}")
        # Яркое запасное поздравление с эмодзи
        if position:
            return (
                f"Коллеги!!! 🙌😄🎉\n\n"
                f"Сегодня отмечает свой день рождения {name}! 🎂🥳🌹🌹🌹🌹🌹🌹\n\n"
                f"{name}, с днём рождения! 🫶❤️ Желаем успехов в работе {position}, море позитива и вдохновения! 💪😁🎈\n\n"
                f"Твои коллеги 🫶🫶🫶"
            )
        else:
            return (
                f"Добрый день, Коллеги!!! 😄🎉\n\n"
                f"Сегодня день рождения у {name}! 🎂🥳🌹🌹🌹\n\n"
                f"{name}, с днём рождения! 🫶 Желаем счастья, здоровья и удачи! 😁🎈🍾\n\n"
                f"Обнимаем и любим! Твои коллеги 🫶❤️"
            )