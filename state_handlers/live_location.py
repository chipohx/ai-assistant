from loguru import logger
logger.info("Adding idle state handler...")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


from telebot import types
import storage

bot = storage.get_value('bot')
state_machine = storage.get_value('state_machine')
csrftoken = storage.get_value('csrftoken')

header = {'X-CSRFToken': csrftoken}
cookies = {'csrftoken': csrftoken}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

from telebot.types import Message, KeyboardButton
import requests
import os

URL = os.getenv("URL")

# Обработка локации (включая живую)
@bot.message_handler(content_types=['location'])
def handle_location(message: Message):
    user_id = message.from_user.id
    sessions = storage.get_value("sessions")
    if message.location.live_period:
        
        if not "location" in sessions[user_id]:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            button = KeyboardButton(text="Давайте начнем! 🚀")
            markup.add(button)

            bot.reply_to(message, "✅ Получена живая локация! Теперь я буду вас отслеживать.", reply_markup=markup)
        sessions[user_id]["location"] = (message.location.latitude, message.location.longitude)
    else:
        bot.reply_to(message, "📍 Спасибо! Но, пожалуйста, отправьте *живую* геолокацию вручную через Telegram.", parse_mode="Markdown")

import time
import threading

# Фоновая задача для отслеживания локаций каждую минуту
def track_locations():
    logger.info("Start sending locations")
    while True:
        time.sleep(30)
        logger.info("Sending locations...")
        sessions = storage.get_value("sessions")
        
        if not sessions:
            continue

        for user_id in sessions.keys():
            if not "location" in sessions[user_id]:
                continue
            lat = sessions[user_id]["location"][0]
            lon = sessions[user_id]["location"][1]
            print(f"[{user_id}] ➤  Широта: {lat}, Долгота: {lon}")

            responce = requests.post(URL + "records/get_location_records", data={"user_id": user_id, "x": lat, "y": lon}, cookies=cookies, headers=header )

            logger.info("Success" if responce else "Failed")

            time.sleep(1)

    
# Запуск фонового трекера
threading.Thread(target=track_locations, daemon=True).start()