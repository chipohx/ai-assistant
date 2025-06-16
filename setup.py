from dotenv import load_dotenv
import os

import telebot
import requests

import storage


if __name__ == "__main__":
    print("This script is intended to be imported as a module, not run directly.")
    exit(1)


# Настройка окружения и загрузка переменных окружения
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

load_dotenv()

TELEGRAMBOT_KEY = os.getenv("TELEGRAMBOT_KEY")
URL = os.getenv("URL")


# Настройка бота и получение CSRF токена для Django приложения
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

bot = telebot.TeleBot(TELEGRAMBOT_KEY)
csrftoken = requests.get(URL).json()['csrf']

if not bot:
    raise ValueError("Bot initialization failed. Please check your TELEGRAMBOT_KEY and URL.")

if not csrftoken:
    raise ValueError("Failed to retrieve CSRF token. Please check your URL.")


# Импорт и настройка хранилища для хранения состояния бота и CSRF токена
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

storage.set_storage('bot', bot)
storage.set_storage('csrftoken', csrftoken)