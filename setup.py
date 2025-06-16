from loguru import logger
logger.info("Setting up bot...")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

from dotenv import load_dotenv
import os

import telebot
import requests

import storage


if __name__ == "__main__":
    logger.error("This script is intended to be imported as a module, not run directly.")
    raise RuntimeError("Please import this script in your main application file.")


# Настройка окружения и загрузка переменных окружения
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
logger.info("Loading environment variables...")

load_dotenv()

TELEGRAMBOT_KEY = os.getenv("TELEGRAMBOT_KEY")
URL = os.getenv("URL")

if not TELEGRAMBOT_KEY or not URL:
    logger.error("Environment variables TELEGRAMBOT_KEY or URL are not set.")
    raise ValueError("Please set the TELEGRAMBOT_KEY and URL environment variables.")

# Настройка бота и получение CSRF токена для Django приложения
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

logger.info("Initializing bot and retrieving CSRF token...")

bot = telebot.TeleBot(TELEGRAMBOT_KEY)
csrftoken = requests.get(URL).json()['csrf']

if not bot:
    raise ValueError("Bot initialization failed. Please check your TELEGRAMBOT_KEY and URL.")

if not csrftoken:
    raise ValueError("Failed to retrieve CSRF token. Please check your URL.")

logger.info("Bot and CSRF token initialized successfully.")


# Импорт и настройка хранилища для хранения состояния бота и CSRF токена
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

storage.set_storage('bot', bot)
storage.set_storage('csrftoken', csrftoken)