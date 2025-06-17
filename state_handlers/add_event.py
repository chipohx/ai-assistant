from loguru import logger
logger.info("Adding setup end state handler...")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


from telebot import types
import storage

bot = storage.get_value('bot')
state_machine = storage.get_value('state_machine')
csrftoken = storage.get_value('csrftoken')


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


def show_event(chat_id):

    sessions = storage.get_value('sessions')
    if not sessions or not chat_id in sessions:
        logger.critical(f"Session not found for chat ID {chat_id}, creating new session")
        exit(1)

    if 'added_reminder' not in sessions[chat_id]:
        bot.send_message(chat_id, "❌ Напоминания не найдены.")
        return

    reminder = sessions[chat_id]['added_reminder']

    text = f"📅 Напоминание\n\n"
    text += reminder['text'].capitalize() + "\n\n"
    text += f"Дата и время: {reminder['datetime'][:16]}\n" if reminder["condition"] == "time" else f"Место: {reminder['address']}\n"
    text += f"Категория: {reminder['category'].capitalize()}"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = types.KeyboardButton("✅ Сохранить напоминание")
    markup.add(button)
    button = types.KeyboardButton("❌ Отменить напоминание")
    markup.add(button)

    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")