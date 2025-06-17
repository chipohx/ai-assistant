from loguru import logger
logger.info("Adding view event data state handler...")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


from telebot import types
import storage

state_machine = storage.get_value('state_machine')
csrftoken = storage.get_value('csrftoken')

bot = storage.get_value('bot')
header = {'X-CSRFToken': csrftoken}
cookies = {'csrftoken': csrftoken}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

import os
import requests

URL = os.getenv("URL")


@bot.callback_query_handler(func=lambda call: ':' in call.data and call.data.startswith("delete:"))
def handle_select_event(call):
    session_id = int(call.message.chat.id)

    sessions = storage.get_value('sessions')

    if not sessions or session_id not in sessions:
        bot.answer_callback_query(call.id, "⛔ Сессия не найдена.")
        return

    event_index = int(call.data.split(":")[1])
    events = sessions[session_id]["event_list"]

    content = {"rec_id": events[event_index]['id']}
    
    responce = requests.post(URL + "records/delete", data=content, headers=header, cookies=cookies)

    if responce.status_code != 200:
        mes = responce.json()
        logger.error(f"Error adding reminder: {mes['message']}")
        bot.send_message(call.message.chat.id, "❌ Не удалось удалить напоминание. Попробуйте еще раз.")
        return

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"🗑 Напоминание удалено 📌",
    )

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: ':' in call.data and call.data.startswith("select:"))
def handle_select_event(call):
    session_id = int(call.message.chat.id)

    sessions = storage.get_value('sessions')

    if not sessions or session_id not in sessions:
        bot.answer_callback_query(call.id, "⛔ Сессия не найдена.")
        return

    event_index = int(call.data.split(":")[1])
    events = sessions[session_id]["event_list"]

    if event_index < 0 or event_index >= len(events):
        bot.answer_callback_query(call.id, "⛔ Неверный индекс события.")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(text="Удалить напоминание", callback_data=f"delete:{event_index}"))


    text = f"📅 Напоминание\n\n"
    text += events[event_index]['text'].capitalize() + "\n\n"
    text += f"Дата и время: {events[event_index]['datetime'][:16].replace('T', ' ')}\n" if events[event_index]["condition"] == "time" else f"Место: {events[event_index]['address']}\n"
    text += f"Категория: {events[event_index]['category'].capitalize()}"

    bot.send_message(call.message.chat.id, text, reply_markup=markup)

    bot.answer_callback_query(call.id)