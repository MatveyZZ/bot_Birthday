import asyncio
import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
from sheets_reader import get_birthdays_today
from ai_generator import generate_congratulations

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=config.TELEGRAM_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

async def send_birthday_greetings():
    """Проверяет дни рождения и отправляет поздравления."""
    try:
        birthdays = get_birthdays_today()
        if not birthdays:
            logging.info("Сегодня нет именинников.")
            return

        for name in birthdays:
            # Генерируем уникальное поздравление с помощью AI
            greeting_text = generate_congratulations(name)
            # Отправляем сообщение в чат
            await bot.send_message(chat_id=config.GROUP_CHAT_ID, text=greeting_text)
            logging.info(f"Поздравление для {name} отправлено!")
            
    except Exception as e:
        logging.error(f"Ошибка при отправке поздравлений: {e}")

# Обработчик команды /start (для проверки работы)
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Бот-поздравитель активен!")

async def on_startup(dp):
    # Запускаем планировщик при старте бота
    scheduler.add_job(send_birthday_greetings, 'cron', hour=9, minute=0) # Каждый день в 09:00
    scheduler.start()
    logging.info("Планировщик запущен.")

async def main():
    # Запуск поллинга
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())