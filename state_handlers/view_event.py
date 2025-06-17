from loguru import logger
logger.info("Adding view event data state handler...")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


from telebot import types
import storage

bot = storage.get_value('bot')


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@bot.callback_query_handler(func=lambda call: ':' in call.data and call.data.startswith("delete:"))
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

    bot.send_message(call.message.chat.id, f"Напоминание успешно удалено!", reply_markup=markup)

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


    text = str(events[event_index])
    bot.send_message(call.message.chat.id, f"Вы выбрали событие:\n\n{text}", reply_markup=markup)

    bot.answer_callback_query(call.id)