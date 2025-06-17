import requests
import json
import re
from datetime import datetime

def parse_reminder_huggingface(text):
    current_datetime = datetime.now()
    print(current_datetime)

    headers = {"Authorization": f"Bearer {'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'}"}

    payload = {
        "messages": [
            {
                "role": "system",
                "content": "Ты парсер напоминаний. Извлекай дату, время и текст. Отвечай строго в JSON-формате, например: {\n\n'action': 'add',\n\n'text': 'забрать дочку из садика', \n\n'category': 'meeting',\n\n'address': 'г. Томск Томский политехнический университет главный корпус',\n\n'datetime': '2023-11-20 09:40',\n\n'done': false,\n\n'condition': 'time'\n\n}. Не добавляй никаких пояснений, только JSON. Action может быть из [add, delete(если нужно удалить конкретную заметку), delete_all(если пришёл запрос на удаление всех заметок), update, all(если пришёл запрос на показ всех заметок)]. Condition может быть [time (напоминание по времени), place (напоминание по месту), timeplace (напоминание по времени и месту)]. Категории: [meeting, shopping, holiday, business]." + f" Текущая дата: {current_datetime}"
            },
            {
                "role": "user",
                "content": text
            }
        ],
        "model": "deepseek/deepseek-v3-0324",
        # "model": "meta-llama/Llama-3-8B-Instruct",
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