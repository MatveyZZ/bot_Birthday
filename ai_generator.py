# ai_generator.py
import logging
import requests
import base64
import config
import urllib3
import re
import pymorphy3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Инициализация морфологического анализатора
morph = pymorphy3.MorphAnalyzer()

def inflect_name(first_name: str, last_name: str, case: str = 'datv') -> str:
    """
    Склоняет имя и фамилию в заданный падеж.
    case: 'nomn' - именительный (кто?), 'datv' - дательный (кому?)
    Возвращает строку вида "Владу Котову"
    """
    try:
        first_parse = morph.parse(first_name)[0]
        last_parse = morph.parse(last_name)[0] if last_name else None
        
        first_inflected = first_parse.inflect({case}).word if first_parse.inflect({case}) else first_name
        last_inflected = last_parse.inflect({case, 'sing'}).word if last_parse and last_parse.inflect({case}) else last_name
        
        if last_name:
            return f"{first_inflected} {last_inflected}".strip()
        else:
            return first_inflected
    except Exception as e:
        logging.warning(f"Не удалось просклонять '{first_name} {last_name}': {e}")
        return f"{first_name} {last_name}".strip()

def get_access_token():
    """Получает access token для GigaChat API."""
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
        if any(phrase.lower() in line.lower() for phrase in disclaimer_phrases):
            continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines).strip()

def generate_congratulations(person: dict) -> str:
    """
    Генерирует персонализированное поздравление.
    person = {
        'full_name': 'Влад Котов',
        'first_name': 'Влад',
        'last_name': 'Котов',
        'position': 'Коммерческий директор',
        'age': 30,
        'is_jubilee': True
    }
    """
    name = person['full_name']
    position = person['position']
    age = person['age']
    is_jubilee = person['is_jubilee']
    first_name = person['first_name']
    last_name = person['last_name']
    
    # Склоняем в дательный падеж (кому?)
    name_datv = inflect_name(first_name, last_name, 'datv')
    
    try:
        token = get_access_token()
        api_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Дополняем системный промпт информацией о юбилее
        jubilee_text = ""
        if is_jubilee and age:
            jubilee_text = f"Сегодня {name} исполняется {age} лет — это ЮБИЛЕЙ! Обязательно упомяни эту круглую дату и сделай акцент на значимости этого события."

        system_prompt = (
            "Ты — профессиональный копирайтер, специализирующийся на создании ярких, "
            "эмоциональных и персонализированных корпоративных поздравлений с днём рождения "
            "для коллег в рабочем чате Telegram. Твоя задача — сгенерировать текст поздравления, "
            "строго следуя образцу, приведённому ниже. "
            "ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙ МНОГО ЭМОДЗИ. "
            "❗️ ВАЖНО: НИ В КОЕМ СЛУЧАЕ НЕ ИСПОЛЬЗУЙ ПОЖЕЛАНИЯ ЗДОРОВЬЯ (слово 'здоровье' и его производные). "
            "❗️ ОБРАЩАЙСЯ К ИМЕНИННИКУ ТОЛЬКО ПО ПОЛНОМУ ИМЕНИ (например, Владислав, а не Влад или Владик). "
            "Вместо пожеланий здоровья делай упор на профессиональные успехи, вдохновение, позитив, удачу, счастье и т.п. "
            f"{jubilee_text}\n"
            "ПРИМЕР ИДЕАЛЬНОГО ПОЗДРАВЛЕНИЯ (скопируй его стиль, длину и обилие эмодзи):\n"
            "---\n"
            "Добрый день, Коллеги!!!😄🎉💃\n"
            "Сегодня день рождения у Елены Булычевой!!!🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹\n\n"
            "Елена, с днём рождения! 🥳🫰❤️\n\n"
            "От всей души поздравляем тебя и хотим сказать огромное спасибо за то, что ты держишь в порядке наши финансы, находишь ответы на самые каверзные вопросы и сохраняешь спокойствие даже в период отчётности!🌹🌹🌹🌹🌹🌹🌹🌹🫶\n\n"
            "Желаем море позитива, гору приятных сюрпризов, океан удачи и миллион поводов для улыбок. Пусть цифры всегда сходятся не только в отчётах, но и в зарплатных ведомостях, а жизнь радует безошибочными «проводками» счастья!🎂🎂🎂🎂🥳🥳🥳🥳\n\n"
            "Обнимаем и любим! Твои коллеги. ❤️🤗\n"
            "---"
        )

        user_prompt = (
            f"Напиши такое же яркое, персонализированное и полное эмодзи поздравление с днём рождения для:\n"
            f"Имя (в именительном падеже, полное): {name}\n"
            f"Имя в дательном падеже (кому? полное): {name_datv}\n"
            f"Должность: {position if position else 'не указана'}\n"
            f"Возраст: {age if age else 'не указан'}\n"
            f"Юбилей: {'Да' if is_jubilee else 'Нет'}\n\n"
            "Используй имя в дательном падеже в обращении (например, 'Владиславу желаем...'). "
            "Обращайся строго по полному имени (не используй уменьшительные формы). "
            "Если это юбилей — обязательно подчеркни важность круглой даты. "
            "❗️ НЕ ИСПОЛЬЗУЙ слова 'здоровье' и пожелания здоровья. "
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
        
        cleaned_text = clean_response(raw_text)
        if not cleaned_text:
            raise ValueError("Пустой ответ после очистки")
        return cleaned_text

    except Exception as e:
        logging.error(f"❌ Ошибка GigaChat для {name}: {e}")
        # Запасное поздравление с учётом склонения
        jub_text = ""
        if age:
            jub_text = f" Поздравляем с {'юбилеем ' if is_jubilee else 'днём рождения'}! Сегодня тебе исполнилось {age} лет!"
        if position:
            return (
                f"Добрый день, Коллеги!!! 😄🎉💃\n\n"
                f"Сегодня день рождения у {name}! 🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹\n\n"
                f"{name_datv}, с {'юбилеем' if is_jubilee else 'днём рождения'}! 🥳🫰❤️{jub_text}\n\n"
                f"Поздравляем тебя и благодарим за отличную работу в должности {position}! "
                f"Пусть каждый день приносит радость, задачи решаются легко, а коллеги ценят и уважают. 💪😁🎈\n\n"
                f"Желаем успехов, вдохновения и море позитива! 🎂🎂🎂🥳🥳🥳\n\n"
                f"Обнимаем и любим! Твои коллеги. ❤️🤗"
            )
        else:
            return (
                f"Добрый день, Коллеги!!! 😄🎉💃\n\n"
                f"Сегодня день рождения у {name}! 🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹🌹\n\n"
                f"{name_datv}, с днём рождения! 🥳🫰❤️{jub_text}\n\n"
                f"Желаем счастья, удачи и всего самого наилучшего! Пусть каждый день будет наполнен улыбками и приятными сюрпризами. 😁🎈🍾💪\n\n"
                f"Обнимаем и любим! Твои коллеги. ❤️🤗"
            )