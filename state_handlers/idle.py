from loguru import logger
logger.info("Adding idle state handler...")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


from telebot import types
from telebot.types import ReplyKeyboardRemove, KeyboardButton
import storage

bot = storage.get_value('bot')
state_machine = storage.get_value('state_machine')
csrftoken = storage.get_value('csrftoken')

header = {'X-CSRFToken': csrftoken}
cookies = {'csrftoken': csrftoken}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

import state_handlers.add_event as add_event
import state_handlers.view_events as view_events
import state_handlers.show_all_events as show_all_events

from text import parse_reminder_huggingface
from voice import parse_reminder_from_audio

import requests
import os

URL = os.getenv("URL")


@bot.message_handler(content_types=['text', 'voice'])
def idle(message):


    sessions = storage.get_value('sessions')
    if not sessions or not message.chat.id in sessions:
        logger.critical(f"Session not found for chat ID {message.chat.id}, creating new session")
        exit(1)

    command = None


    if state_machine.get_state(message.chat.id) == "Greetings":

        if not "location" in sessions[message.chat.id]:
            bot.send_message(message.chat.id, "Пожалуйста, отправьте свою живую локацию")
            return
        elif message.text == "Синхронизировать Google Calendar":

            responce = requests.get(URL + "login", params={"user_id": message.chat.id})

            if responce.status_code == 200:
                auth_url = responce.json()["url"]

                text = "Для синхронизации Google Calendar перейдите по ссылке: \n\n" + f"<a href='{auth_url}'>{'Google Autorization'}</a>"

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                button = KeyboardButton(text="Давайте начнем! 🚀")
                markup.add(button)

                bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")

                return
            else:
                logger.error(responce.json())

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                button = KeyboardButton(text="Давайте начнем! 🚀")
                markup.add(button)
                button = KeyboardButton(text="Синхронизировать Google Calendar")
                markup.add(button)

                bot.send_message(message.chat.id, "Не удалось выполнить синхронизацию... попробуйте еще раз", reply_markup=markup)
                return
        else:
            state_machine.trigger(message.from_user.id, "continue")

    if message.text == "Давайте начнем! 🚀" or message.text == "Назад":
        bot.send_message(message.chat.id, "🕒 Отлично! Напишите его текст или отправьте аудио с напоминанием. \n\nЕсли захотите удалить напоминание, то скажите \"Удалить напоминание на завтра...\"\n\n Если захотите получить список напоминаний, то скажите \"Покажи все напоминания\"", reply_markup=ReplyKeyboardRemove())
        return
    elif message.text == "❌ Отменить напоминание":
        bot.send_message(message.chat.id, "❌ Напоминание отменено", reply_markup=ReplyKeyboardRemove())
        return
    elif message.text == "✅ Сохранить напоминание":

        bot.send_message(message.chat.id, "💾 Сохраняю напоминание...", reply_markup=ReplyKeyboardRemove())
        
        content = sessions[message.chat.id]['added_reminder']
        content['user_id'] = message.chat.id
        
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
        bot.send_message(message.chat.id, "Обработка голоса...")
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
        return

    if command["action"] == "delete":
        

        message_id = bot.send_message(message.chat.id, "Получаю список напоминаний...")

        content = {"text": command["text"]}
        content['user_id'] = message.chat.id
        
        responce = requests.get(URL + "records/get_similar", params=content, headers=header, cookies=cookies)

        if responce.status_code != 200:
            mes = responce.json()
            logger.error(f"Error adding reminder: {mes['message']}")
            bot.send_message(message.chat.id, "❌ Не удалось получить напоминания. Попробуйте еще раз.")
            return
        
        reminders = responce.json()
        sessions[message.chat.id]['event_list'] = reminders['recs']
        storage.set_storage('sessions', sessions)

        view_events.show_events(message.chat.id)

        return
    

    if command["action"] == "show":
        
        content = {"user_id": message.chat.id}
        
        responce = requests.get(URL + "records/all", params=content, headers=header, cookies=cookies)

        if responce.status_code != 200:
            mes = responce.json()
            logger.error(f"Error adding reminder: {mes['message']}")
            bot.send_message(message.chat.id, "❌ Не удалось получить напоминания. Попробуйте еще раз.")
            return
        
        reminders = responce.json()["recs"]
        sessions[message.chat.id]["event_list"] = reminders
        storage.set_storage('sessions', sessions)

        show_all_events.show_all_events(message.chat.id)

        return

    if command["action"] == "delete_all":
        bot.send_message(message.chat.id, "Функционал удаления всех сообщений был упущен 🚽")
        return

    bot.send_message(message.chat.id, "Команда не распознана 🧻")