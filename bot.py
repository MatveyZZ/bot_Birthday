# bot.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

import config
from sheets_reader import get_birthdays_today
from ai_generator import generate_congratulations

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TELEGRAM_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

async def send_birthday_greetings():
    logging.info("Проверяю дни рождения...")
    try:
        birthdays = get_birthdays_today()
        if not birthdays:
            logging.info("Сегодня именинников нет.")
            return
        for name in birthdays:
            greeting = generate_congratulations(name)
            await bot.send_message(chat_id=config.GROUP_CHAT_ID, text=greeting)
            logging.info(f"Поздравление для {name} отправлено!")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")

async def main():
    scheduler.add_job(send_birthday_greetings, 'cron', hour=9, minute=0)
    scheduler.start()
    logging.info("Бот запущен и ждёт своего часа...")
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())