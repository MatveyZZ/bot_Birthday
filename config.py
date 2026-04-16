# config.py

# --- Telegram ---
TELEGRAM_TOKEN = "8798100864:AAHK91xBHMeX_WD3_o58kfqfY0uRS-Rso3s"
GROUP_CHAT_ID = -1001234567890 # ID вашего чата

# --- Google Таблицы ---Й
SHEET_ID = "1Oxrwlwh9Gnb_vGyl8IsC_E-9oXs7XNllFpHGO01V9Ms"

# --- GigaChat API ---
GIGACHAT_CLIENT_ID = "019d94f6-0d1e-774a-adb6-8d748a73dc0d"
GIGACHAT_CLIENT_SECRET = "d66d479f-f04e-4668-96ae-195d6258c350"
GIGACHAT_SCOPE = "GIGACHAT_API_PERS" # Пространство для физлиц

# config.py
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "0"))

SHEET_ID = os.getenv("SHEET_ID")

GIGACHAT_CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")
GIGACHAT_SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")