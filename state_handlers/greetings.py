from loguru import logger
logger.info("Adding greetings handler...")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


from telebot import types
import storage

bot = storage.get_value('bot')
state_machine = storage.get_value('state_machine')
csrftoken = storage.get_value('csrftoken')


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


@bot.message_handler(commands=['start'])
def send_welcome(message):

    # Текст приветствия и условий
    welcome_text = (
        "👋 Приветствую вас в боте напоминаний!\n\n"
        "📝 Этот бот поможет вам создавать напоминания и управлять ими удобно и просто.\n\n"
        "🔒 Условия пользования:\n"
        "— Бот может использовать геолокацию для привязки напоминаний к месту\n"
        "— Доступна авторизация через Google для синхронизации, но это **необязательно**\n\n"
        "Вы можете использовать все функции и без этих опций.\n"
        "Готовы продолжить?"
    )

    # Создание клавиатуры с кнопкой "Продолжить"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = types.KeyboardButton("✅ Продолжить")
    markup.add(button)

    # Отправка сообщения
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)