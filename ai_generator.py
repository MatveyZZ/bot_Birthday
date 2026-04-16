# ai_generator.py
import logging
from gigachat import GigaChat
import config

def generate_congratulations(name: str, position: str = "") -> str:
    """
    Генерирует персонализированное поздравление с днём рождения через GigaChat.
    """
    try:
        # Формируем prompt с учётом должности
        if position and position.strip():
            prompt = (f"Напиши короткое, оригинальное и тёплое поздравление с днём рождения для {name}. "
                      f"Он(а) работает {position}. Учти это в поздравлении, но не перегружай. "
                      f"На русском языке, без лишних деталей.")
        else:
            prompt = f"Напиши короткое, оригинальное и тёплое поздравление с днём рождения для {name}. На русском языке, без лишних деталей."

        # Правильный способ авторизации для физических лиц
        with GigaChat(
            credentials=config.GIGACHAT_CLIENT_SECRET,
            scope=config.GIGACHAT_SCOPE,
            verify_ssl_certs=False
        ) as client:
            response = client.chat(prompt)
            return response.choices[0].message.content

    except Exception as e:
        logging.error(f"Ошибка GigaChat: {e}")
        # Запасное поздравление
        if position:
            return f"{name}, с днём рождения! Успехов в работе {position}!"
        else:
            return f"{name}, с днём рождения! Счастья и здоровья!"