# ai_generator.py
import logging
import requests
import base64
import config
import urllib3
import pymorphy3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Инициализация морфологического анализатора
morph = pymorphy3.MorphAnalyzer()

def inflect_name(first_name: str, last_name: str, case: str = 'datv') -> str:
    """
    Склоняет имя и фамилию в заданный падеж.
    case: 'nomn' - именительный (кто?), 'datv' - дательный (кому?)
    Возвращает строку вида "Владиславу Котову"
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
        "чувствительные темы могут быть ограничены",
        "Как и любая языковая модель",
        "дисклеймер"
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
        'full_name': 'Владислав Котов',
        'first_name': 'Владислав',
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

        age_info = ""
        if age:
            age_info = f" Ему исполняется {age} лет."
            if is_jubilee:
                age_info += " Это юбилей!"

        system_prompt = (
            "Ты помогаешь писать тёплые и весёлые поздравления с днём рождения для коллег. "
            "Пиши в корпоративном стиле, с эмодзи. Обращайся по полному имени, на 'ты' или 'Вы' в зависимости от должности. "
            "Не используй слово 'здоровье'. "
            "Пример:\n"
            "Добрый день, Коллеги!!! 😄🎉\n"
            "Сегодня день рождения у Елены Булычевой!!! 🌹🌹🌹\n"
            "Елена, с днём рождения! 🥳❤️\n"
            "Спасибо за твой вклад в финансы! Желаем успехов и отличного настроения! 🎂🎂🎂\n"
            "Обнимаем, твои коллеги. 🤗"
        )

        user_prompt = (
            f"Напиши поздравление для {name} ({position if position else 'сотрудник'})."
            f"{age_info} "
            f"В дательном падеже: {name_datv}. "
            "Сделай текст ярким, с эмодзи, без дисклеймеров."
        )

        payload = {
            "model": "GigaChat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 1500,
            "top_p": 0.9
        }

        resp = requests.post(api_url, headers=headers, json=payload, verify=False)
        resp.raise_for_status()
        raw_text = resp.json()["choices"][0]["message"]["content"]
        logging.info(f"Полный ответ GigaChat:\n{raw_text}")

        # Если ответ — только дисклеймер, переходим к запасному варианту
        if any(phrase in raw_text.lower() for phrase in [
            "не обладает собственным мнением",
            "генеративные языковые модели",
            "разговоры на чувствительные темы"
        ]):
            logging.warning("GigaChat вернул только дисклеймер, используем запасное поздравление")
            raise ValueError("Ответ содержит только дисклеймер")

        cleaned = clean_response(raw_text)
        return cleaned if cleaned else raw_text

    except Exception as e:
        logging.error(f"❌ Ошибка GigaChat для {name}: {e}")
        # Запасное яркое поздравление
        jub_text = ""
        if age:
            jub_text = f" Сегодня тебе исполнилось {age} лет!"
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
                f"Желаем счастья, удачи и всего самого наилучшего! 😁🎈🍾💪\n\n"
                f"Обнимаем и любим! Твои коллеги. ❤️🤗"
            )