from loguru import logger
logger.info("Adding idle state handler...")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


from telebot import types
import storage

bot = storage.get_value('bot')
state_machine = storage.get_value('state_machine')
csrftoken = storage.get_value('csrftoken')


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

import state_handlers.add_event as add_event
from text import parse_reminder_huggingface
from voice import parse_reminder_from_audio

import requests
import os

URL = os.getenv("URL")


@bot.message_handler(content_types=['text', 'voice'])
def idle(message):

    if state_machine.get_state(message.from_user.id) != 'Idle':
        state_machine.trigger(message.from_user.id, "continue")

    sessions = storage.get_value('sessions')
    if not sessions or not message.chat.id in sessions:
        logger.critical(f"Session not found for chat ID {message.chat.id}, creating new session")
        exit(1)

    command = None

    if message.text == "Да! Давайте начнем! 🚀":
        bot.send_message(message.chat.id, "🕒 Отлично! Напишите его текст или отправьте аудио с напоминанием.")
        return
    elif message.text == "❌ Отменить напоминание":
        bot.send_message(message.chat.id, "❌ Напоминание отменено")
        return
    elif message.text == "✅ Сохранить напоминание":
        content = sessions[message.chat.id]['added_reminder']
        content['user_id'] = message.chat.id
        header = {'X-CSRFToken': csrftoken}
        cookies = {'csrftoken': csrftoken}

        responce = requests.post(URL + "records/add", data=content, headers=header, cookies=cookies)

        if responce.status_code != 200:
            mes = responce.json()
            logger.error(f"Error adding reminder: {mes['message']}")
            bot.send_message(message.chat.id, "❌ Не удалось сохранить напоминание. Попробуйте еще раз.")
            return
        bot.send_message(message.chat.id, "✅ Напоминание успешно сохранено!")
        return
    
    elif message.content_type == 'text':
        command = parse_reminder_huggingface(message.text)
        logger.info(f"User {message.from_user.id} added text command: {command}")
    elif message.content_type == 'voice':

        voice = message.voice
        file_info = bot.get_file(voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Формируем путь с именем файла
        file_name = f"voice.ogg"
        with open(file_name, 'wb') as f:
            f.write(downloaded_file)
        
        command = parse_reminder_from_audio(file_name)
        # command = decription_text.parse_reminder_huggingface(raw_command)
        logger.info(f"User {message.from_user.id} added audio command: {command}")


    if not command:
        bot.send_message(message.chat.id, "❌ Не удалось распознать команду. Попробуйте еще раз.")
        return
    
    if command["action"] == "add":
        sessions[message.chat.id]['added_reminder'] = command
        storage.set_storage('sessions', sessions)
        add_event.show_event(message.chat.id)

    if command["action"] == "delete":
        pass

    if command["action"] == "view":
        pass