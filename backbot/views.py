from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.middleware.csrf import get_token

import requests
from datetime import datetime
import json
import re


URL = "http://localhost:8000"

def post_db(url, content):
    csrftoken = requests.get(url).json()['csrf']
    
    header = {'X-CSRFToken': csrftoken}
    cookies = {'csrftoken': csrftoken}

    ans = requests.post(url, data=content, headers=header, cookies=cookies).json()
    return ans
    
    

def index(request):
    content = {'message' : 'hello', 'csrf': get_token(request)}
    if request.method == 'POST':
        
        ans = preprosess_message(request.POST['message'])
        ans['user_id'] = request.POST['user_id']
        
        resp = post_db(URL + '/records/add', ans)
        return JsonResponse(resp)
    
    return JsonResponse(content)

def preprosess_message(text):
    try:
        reminder = "Создай заметку на послезавтра на 6 часов вечера забрать дочку из садика"
        parsed_data = parse_reminder_huggingface(reminder)

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
    print(current_datetime)

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

