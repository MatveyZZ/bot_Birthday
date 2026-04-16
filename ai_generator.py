import google.generativeai as genai

import config

# Настройка API ключа Gemini
genai.configure(api_key=config.GEMINI_API_KEY)

# Выбор модели (Gemini 2.5 Flash бесплатен и быстр)
model = genai.GenerativeModel('gemini-2.5-flash')

def generate_congratulations(name: str) -> str:
    """
    Генерирует персонализированное поздравление с днём рождения.
    """
    try:
        prompt = f"Напиши короткое, оригинальное и тёплое поздравление с днём рождения для {name}. На русском языке, без лишних деталей."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Ошибка при генерации текста: {e}")
        # Возвращаем запасное поздравление
        return f"С днём рождения, {name}! Всего самого наилучшего!"