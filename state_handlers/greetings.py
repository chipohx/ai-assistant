from loguru import logger
logger.info("Adding greetings handler...")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message
import storage

bot = storage.get_value('bot')
state_machine = storage.get_value('state_machine')
csrftoken = storage.get_value('csrftoken')


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


@bot.message_handler(commands=['start'])
def send_welcome(message):

    user_id = message.from_user.id

    if state_machine.get_state(user_id):
        logger.info(f"User {user_id} already has a state, skipping greetings.")
        bot.send_message(message.chat.id, "🚽")
        return
    
    state_machine.set_initial_state(user_id, 'Greetings')

    sessions = storage.get_value('sessions')
    if not sessions:
        logger.info("Creating new sessions storage")
        sessions = {}
    if not message.chat.id in sessions:
        logger.info(f"Creating new session for chat ID {message.chat.id}")
        sessions[message.chat.id] = {'event_list': [], 'current_page': 0, 'current_event': None}
        storage.set_storage('sessions', sessions)

    # Текст приветствия и условий
    welcome_text = (
        "👋 Приветствую вас в боте напоминаний!\n\n"
        "📝 Этот бот поможет вам создавать напоминания и управлять ими удобно и просто.\n\n"
        "🔒 Условия пользования:\n"
        "— Бот может использовать геолокацию для привязки напоминаний к месту\n"
        "— Доступна авторизация через Google для синхронизации, но это необязательно\n\n"
        "Пожалуйста, нажмите кнопку ниже, чтобы отправить вашу геолокацию."
        "⚠️ После этого, отправьте живую геолокацию вручную\n"
        "Откройте вложения 📎 -> Геопозиция -> Отправить мою живую геолокацию 🛰️.\n\n"
        "Я буду отслеживать ваше местоположение в реальном времени."
    )

    # Создание клавиатуры с кнопкой "Продолжить"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    location_button = KeyboardButton(text="📍 Отправить локацию", request_location=True)
    markup.add(location_button)

    # Отправка сообщения
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)
