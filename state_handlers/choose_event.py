from loguru import logger
logger.info("Adding choose event handler...")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


from telebot import types
import storage

bot = storage.get_value('bot')

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


# @bot.message_handler(commands=['start'])
# def start(message):

#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     btn1 = types.KeyboardButton("👋 Привет! Я бот для создания напоминаний! ")
#     markup.add(btn1)
#     bot.send_message(message.from_user.id, "👋 Привет! Я твой бот-помошник!", reply_markup=markup)