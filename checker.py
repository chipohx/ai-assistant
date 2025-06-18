import telebot
from telebot import types
import requests

from dotenv import load_dotenv
import os
from time import sleep

load_dotenv()
TOKEN=os.getenv("TOKEN")
URL='https://feebly-settled-killifish.cloudpub.ru'

csrftoken = requests.get(URL+"/csrf").json()['csrf']
header = {'X-CSRFToken': csrftoken}
cookies = {'csrftoken': csrftoken}

while True:
    sleep(60)
    recs = requests.get(URL+"/records/get_passed_records").json()['recs']
    
    if not recs: continue
    for rec in recs:

        CHAT_ID = rec[1]

        TEXT = (
                f"🕒 Напоминание!\n" +
                f"📅 {rec[4]}\n" + 
                f"📝 Не забудь: {rec[2].capitalize()}.\n" +
                f"📌 Категория: {rec[3].capitalize()}\n" +
                f"✨ Хорошего дня!"
            )
        

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": TEXT
        }

        response = requests.post(url, data=payload)
        if response.status_code == 200:
            content = {"rec_id": rec[0]}
            mes = requests.post(URL + '/records/delete', data=content, headers=header, cookies=cookies)
    


