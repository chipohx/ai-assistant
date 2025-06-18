from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.middleware.csrf import get_token

import requests
from datetime import datetime
import json
import re
from google_auth_oauthlib.flow import Flow
import os, pickle
from dotenv import load_dotenv

load_dotenv()

URL = "http://localhost:8000"

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/calendar"]
REDIRECT_URI = "https://feebly-settled-killifish.cloudpub.ru/oauth2callback"
TOKEN=os.getenv("TOKEN")

user_tokens = {}
pending_flows = {}

def post_db(url, content):
    csrftoken = requests.get(url).json()['csrf']
    
    header = {'X-CSRFToken': csrftoken}
    cookies = {'csrftoken': csrftoken}

    ans = requests.post(url, data=content, headers=header, cookies=cookies).json()
    return ans
def get_db(url, content):
    return requests.get(url, params=content)

def get_csrf(request):
    content = {'csrf': get_token(request)}
    return JsonResponse(content)

def index(request):
    ans = preprosess_message(request.POST['message'])
    ans['user_id'] = request.POST['user_id']
    return JsonResponse(ans)


def send_message(CHAT_ID, TEXT):
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": TEXT
    }
    response = requests.post(url, data=payload)
    return response

def login(request):
    user_id = request.GET['user_id']

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    # 📌 Используем user_id как state
    auth_url, _ = flow.authorization_url(
        prompt='consent',
        access_type='offline',
        include_granted_scopes='true',
        state=str(user_id)
    )

    pending_flows[user_id] = flow
    return JsonResponse({"url": auth_url})

# def login(request):
#     user_id = request.GET['user_id']
#     print("in login", user_id)
#     flow = Flow.from_client_secrets_file(
#         CLIENT_SECRETS_FILE,
#         scopes=SCOPES,
#         redirect_uri=REDIRECT_URI
#     )
#     auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')
#     print("in login", user_id)
#     print("_", _)
#     user_tokens[user_id] = flow
#     return JsonResponse({"url": auth_url})


def oauth2callback(request):
    state = request.GET['state']
    code = request.GET['code']
  
    if not state or not code:
        return render(request, 'backbot/unsuccessful_reg.html')

    try:
        user_id = state
    except ValueError:
        return render(request, 'backbot/unsuccessful_reg.html')
    
    flow = pending_flows.get(user_id)
    if not flow:
        return render(request, 'backbot/unsuccessful_reg.html')
    
    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials

        # 💾 Сохраняем токен
        os.makedirs("tokens", exist_ok=True)
        with open(f"tokens/{user_id}.pickle", "wb") as token_file:
            pickle.dump(credentials, token_file)
        send_message(user_id, "✅ Вы успешно авторизовались!")
        del pending_flows[user_id]  # очищаем память
        return render(request, 'backbot/successful_reg.html')
        return HttpResponse("Авторизация завершена. Можете вернуться в Telegram.")
    except Exception as e:
        return render(request, 'backbot/unsuccessful_reg.html')
    
# def oauth2callback(request):
#     state = request.GET['state']
#     code = request.GET['code']
#     print("USer tokens", user_tokens)
#     print("state", state)

#     for user_id, flow in user_tokens.items():
#         print("In oauth", user_id)
#         flow.fetch_token(code=code)
#         credentials = flow.credentials
#         # Сохраняем токен
#         with open(f"tokens/{user_id}.pickle", "wb") as token_file:
#             pickle.dump(credentials, token_file)
#         send_message(user_id, "✅ Вы успешно авторизовались!")
#         #bot.send_message(user_id, "✅ Вы успешно авторизовались!")
#         return HttpResponse("Авторизация завершена. Можете вернуться в Telegram.")
#     return HttpResponse("Ошибка авторизации")


# =======================================================
def preprosess_message(text):
    try:
        parsed_data = parse_reminder_huggingface(text)

        return parsed_data
        # # Выводим все поля из JSON
        # print("Распарсенные данные:")
        # print(f"Действие: {parsed_data.get('action', 'не указано')}")
        # print(f"Текст: {parsed_data.get('text', 'не указан')}")
        # print(f"Категория: {parsed_data.get('category', 'не указана')}")
        # print(f"Локация: {parsed_data.get('location', 'не указана')}")
        #
        # if 'datetime' in parsed_data:
        #     try:
        #         reminder_time = datetime.strptime(parsed_data['datetime'], "%Y-%m-%d %H:%M")
        #         print(f"Дата и время: {reminder_time}")
        #     except ValueError:
        #         print(f"Неверный формат даты: {parsed_data['datetime']}")
        # else:
        #     print("Дата и время: не указаны")
        #
        # print(f"Статус выполнения: {parsed_data['done']}")
        # print(f"Условие напоминания: {parsed_data.get('condition', 'None')}")

    except KeyError as e:
        return f"В ответе отсутствует ожидаемый ключ: {e}. Полный ответ: {parsed_data}"
    except Exception as e:
        return f"Произошла ошибка: {str(e)}"

def parse_reminder_huggingface(text):
    current_datetime = datetime.now()
    

    headers = {"Authorization": f"Bearer {'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'}"}

    payload = {
        "messages": [
            {
                "role": "system",
                "content": "Ты парсер напоминаний. Извлекай дату, время и текст. Отвечай строго в JSON-формате, например: {\n\n'action': 'add',\n\n'text': 'забрать дочку из садика', \n\n'category': 'meeting',\n\n'address': 'г. Томск Томский политехнический университет главный корпус',\n\n'datetime': '2023-11-20 09:40',\n\n'done': false,\n\n'condition': 'time'\n\n}. Не добавляй никаких пояснений, только JSON. Action может быть add, delete и update. Condition может быть time (напоминание по времени), place (напоминание по месту) и timeplace (напоминание по времени и месту). Категории: meeting, shopping, holiday, business." + f" Текущая дата: {current_datetime}"
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "model": "deepseek/deepseek-v3-0324",
        #"model": "meta-llama/Llama-3-8B-Instruct",
    }

    response = requests.post(
        "https://router.huggingface.co/novita/v3/openai/chat/completions",
        headers=headers,
        json=payload,
    )

    if response.status_code == 200:
        result = response.json()["choices"][0]["message"]["content"]

        # Пытаемся извлечь JSON из ответа
        try:
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                raise ValueError(f"Не найден JSON в ответе: {result}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка парсинга JSON. Ответ модели: {result}") from e
    else:
        raise Exception(f"Ошибка API. Код: {response.status_code}. Текст: {response.text}")

