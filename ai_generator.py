# ai_generator.py
import logging
import requests
import uuid
import config

def get_access_token():
    """Получает access token для GigaChat API."""
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        "Authorization": f"Bearer {config.GIGACHAT_CLIENT_SECRET}",
        "RqUID": str(uuid.uuid4()),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"scope": config.GIGACHAT_SCOPE}
    try:
        # verify=False только для обхода проблем с сертификатами в GitHub Actions
        resp = requests.post(url, headers=headers, data=data, verify=False)
        resp.raise_for_status()
        return resp.json()["access_token"]
    except Exception as e:
        logging.error(f"❌ Не удалось получить токен GigaChat: {e}")
        raise

def generate_congratulations(name: str, position: str = "") -> str:
    try:
        token = get_access_token()
        api_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        if position and position.strip():
            prompt = (f"Напиши короткое, оригинальное и тёплое поздравление с днём рождения для {name}. "
                      f"Он(а) работает {position}. Учти это в поздравлении, но не перегружай. "
                      f"На русском языке, без лишних деталей.")
        else:
            prompt = f"Напиши короткое, оригинальное и тёплое поздравление с днём рождения для {name}. На русском языке, без лишних деталей."

        payload = {
            "model": "GigaChat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 300
        }

        resp = requests.post(api_url, headers=headers, json=payload, verify=False)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    except Exception as e:
        logging.error(f"❌ Ошибка GigaChat: {e}")
        # Запасное поздравление
        if position:
            return f"{name}, с днём рождения! Успехов в работе {position}!"
        else:
            return f"{name}, с днём рождения! Счастья и здоровья!"