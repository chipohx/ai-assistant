from loguru import logger
logger.info("Adding setup end state handler...")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


from telebot import types
import storage

bot = storage.get_value('bot')
state_machine = storage.get_value('state_machine')
csrftoken = storage.get_value('csrftoken')


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


@bot.message_handler(func=lambda message: message.text == "✅ Продолжить")
def handle_continue(message):

    user_id = message.from_user.id

    if not state_machine.get_state(user_id) or state_machine.get_state(user_id) != 'Greetings':
        bot.send_message(message.chat.id, "Произошел какой-то хехех. Срочно дебажить! 🚽")
        logger.error(f"User {user_id} tried to continue without being in the 'Greetings' state.")
        return
    
    state_machine.trigger(user_id, "continue")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = types.KeyboardButton("Да! Давайте начнем! 🚀")
    markup.add(button)

    bot.send_message(message.chat.id, "Отлично! Давайте создадим ваше первое напоминание. 🕒\n\nГотовы?", reply_markup=markup)