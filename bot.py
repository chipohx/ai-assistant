import telebot
from telebot import types
import requests

from dotenv import load_dotenv
import os

TELEGRAMBOT_KEY='7149122758:AAFPExYYBW1YLICqo76wx9O-UNOXJ7_wtNU'
URL='https://feebly-settled-killifish.cloudpub.ru/'

load_dotenv()
bot = telebot.TeleBot(TELEGRAMBOT_KEY)



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

state = "idle"
# Список состояний:
# - 
csrftoken = requests.get(URL).json()['csrf']
header = {'X-CSRFToken': csrftoken}
cookies = {'csrftoken': csrftoken}

@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Привет! Я бот для создания напоминаний! ")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "👋 Привет! Я твой бот-помошник!", reply_markup=markup)

@bot.message_handler(commands=['all'])
def get_all_records(message):
    mes = requests.get(URL+"/records/all", params={"user_id": message.from_user.id}).json()
    bot.send_message(message.from_user.id, str(mes['recs']))


@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    if message.text == '👋 Поздороваться':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True) #создание новых кнопок
        btn1 = types.KeyboardButton('Как стать автором на Хабре?')
        btn2 = types.KeyboardButton('Правила сайта')
        btn3 = types.KeyboardButton('Советы по оформлению публикации')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, '❓ Задайте интересующий вас вопрос', reply_markup=markup) #ответ бота

    else:
               
        content = {"message": message.text, "user_id": message.from_user.id}
        

        mes = requests.post(URL, data=content, headers=header, cookies=cookies).json()
        bot.send_message(message.from_user.id, mes['message'])


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть