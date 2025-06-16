from loguru import logger
logger.info("Adding setup end state handler...")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


from telebot import types
import storage

bot = storage.get_value('bot')
state_machine = storage.get_value('state_machine')
csrftoken = storage.get_value('csrftoken')


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

from random import choice

funny_responses = (
    "Гениально. Жаль, что я ничего не понял 🤡",
    "Интересный набор слов… а теперь, пожалуйста, по-человечески 🧐",
    "Ты серьёзно? Даже я — бот, и то такое не отправил бы",
    "Это был план саботажа или просто промах мимо клавиш? 🎯",
    "Если это должно было впечатлить — не вышло 😎",
    "Ты случайно в меня пишешь, а не в гугл?",
    "Вот это загадка! А теперь давай без ребусов, ладно?",
    "Ты как будто с ИИ спорить решил. Смело, но бесполезно 😏",
    "Я бы сказал, что это красиво... но мне запретили врать",
    "Ёкарный бабай! 🚽\n\nТочно это хотели написать?"
)

@bot.message_handler(func=lambda message: True)
def fallback_handler(message):
    bot.send_message(message.chat.id, choice(funny_responses))
