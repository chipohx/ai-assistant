import telebot
from telebot import types
import requests

bot = telebot.TeleBot('7149122758:AAFPExYYBW1YLICqo76wx9O-UNOXJ7_wtNU')

@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Поздороваться")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "👋 Привет! Я твой бот-помошник!", reply_markup=markup)

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
        URL = 'http://localhost:8000'

        csrftoken = requests.get(URL).json()['csrf']
        
        content = {"message": message.text, "user_id": message.from_user.id}
        header = {'X-CSRFToken': csrftoken}
        cookies = {'csrftoken': csrftoken}

        mes = requests.post(URL, data=content, headers=header, cookies=cookies).json()
        bot.send_message(message.from_user.id, mes['message'])

bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть