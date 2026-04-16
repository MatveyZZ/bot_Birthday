# ai_generator.py
import logging
from gigachat import GigaChat
import config

def generate_congratulations(name: str) -> str:
    try:
        with GigaChat(
            credentials=config.GIGACHAT_CLIENT_SECRET,
            scope=config.GIGACHAT_SCOPE,
            client_id=config.GIGACHAT_CLIENT_ID,
            verify_ssl_certs=False,
        ) as client:
            prompt = f"Напиши короткое, оригинальное и тёплое поздравление с днём рождения для {name}. На русском языке, без лишних деталей."
            response = client.chat(prompt)
            return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Ошибка GigaChat: {e}")
        return f"{name}, с днём рождения! Счастья и здоровья!"