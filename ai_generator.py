# ai_generator.py
import logging
import requests
import base64
import config
import urllib3
import re

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

def clean_response(text: str) -> str:
    """Удаляет из ответа типовые дисклеймеры GigaChat."""
    # Список ключевых фраз, при обнаружении которых удаляется весь абзац или строка
    disclaimer_phrases = [
        "GigaChat не обладает",
        "генеративные языковые модели",
        "нейросетевой моделью",
        "разговоры на некоторые темы временно ограничены",
        "не обладает собственным мнением",
        "обобщением информации, находящейся в открытом доступе",
        "избежать ошибок и неправильного толкования",
        "чувствительные темы могут быть ограничены"
    ]
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Если строка содержит любую из фраз, пропускаем её
        if any(phrase.lower() in line.lower() for phrase in disclaimer_phrases):
            continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines).strip()

def generate_congratulations(name: str, position: str = "") -> str:
    try:
        token = get_access_token()
        api_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        system_prompt = (
            "Ты — профессиональный копирайтер, специализирующийся на создании ярких, "
            "эмоциональных и персонализированных корпоративных поздравлений с днём рождения "
            "для коллег в рабочем чате Telegram. Твоя задача — сгенерировать текст поздравления, "
            "строго следуя образцу, приведённому ниже. "
            "ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙ МНОГО ЭМОДЗИ. "
            "ПРИМЕР ИДЕАЛЬНОГО ПОЗДРАВЛЕНИЯ (скопируй его стиль, длину и обилие эмодзи):\n"
            "---\n"
            "Добрый день, Коллеги!!!😄🎉💃\n"
            "Сегодня день рождения у Елены Булычевой!!!🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹\n\n"
            "Лена, с днём рождения! 🥳🫰❤️\n\n"
            "От всей души поздравляем тебя и хотим сказать огромное спасибо за то, что ты держишь в порядке наши финансы, находишь ответы на самые каверзные вопросы и сохраняешь спокойствие даже в период отчётности!🌹🌹🌹🌹🌹🌹🌹🌹🫶\n\n"
            "Желаем море позитива, гору приятных сюрпризов, океан удачи и миллион поводов для улыбок. Пусть цифры всегда сходятся не только в отчётах, но и в зарплатных ведомостях, а жизнь радует безошибочными «проводками» счастья!🎂🎂🎂🎂🥳🥳🥳🥳\n\n"
            "Обнимаем и любим! Твои коллеги. ❤️🤗\n"
            "---"
        )

        user_prompt = (
            f"Напиши такое же яркое, персонализированное и полное эмодзи поздравление с днём рождения для:\n"
            f"Имя: {name}\n"
            f"Должность: {position if position else 'не указана'}\n\n"
            "Обязательно следуй структуре примера. Не добавляй никаких дисклеймеров или примечаний от лица GigaChat."
        )

        payload = {
            "model": "GigaChat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 2000,
            "top_p": 0.9
        }

        resp = requests.post(api_url, headers=headers, json=payload, verify=False)
        resp.raise_for_status()
        raw_text = resp.json()["choices"][0]["message"]["content"]
        logging.info(f"Ответ GigaChat (первые 200 символов): {raw_text[:200]}...")
        
        # Очищаем от дисклеймеров
        cleaned_text = clean_response(raw_text)
        if not cleaned_text:
            # Если после очистки ничего не осталось, используем запасной вариант
            raise ValueError("Пустой ответ после очистки")
        return cleaned_text

    except Exception as e:
        logging.error(f"❌ Ошибка GigaChat для {name}: {e}")
        # Запасное яркое поздравление
        if position:
            return (
                f"Добрый день, Коллеги!!! 😄🎉💃\n\n"
                f"Сегодня день рождения у {name}! 🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹\n\n"
                f"{name}, с днём рождения! 🥳🫰❤️\n\n"
                f"Поздравляем тебя и благодарим за отличную работу в должности {position}! "
                f"Пусть каждый день приносит радость, задачи решаются легко, а коллеги ценят и уважают. 💪😁🎈\n\n"
                f"Желаем успехов, вдохновения и море позитива! 🎂🎂🎂🥳🥳🥳\n\n"
                f"Обнимаем и любим! Твои коллеги. ❤️🤗"
            )
        else:
            return (
                f"Добрый день, Коллеги!!! 😄🎉💃\n\n"
                f"Сегодня день рождения у {name}! 🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹\n\n"
                f"{name}, с днём рождения! 🥳🫰❤️\n\n"
                f"Желаем счастья, здоровья, удачи и всего самого наилучшего! Пусть каждый день будет наполнен улыбками и приятными сюрпризами. 😁🎈🍾💪\n\n"
                f"Обнимаем и любим! Твои коллеги. ❤️🤗"
            )