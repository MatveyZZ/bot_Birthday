# bot.py
import asyncio
import logging
from aiogram import Bot
import config
from sheets_reader import get_birthdays_today
from ai_generator import generate_congratulations

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=config.TELEGRAM_TOKEN)
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
            await asyncio.sleep(1)  # пауза между сообщениями
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())