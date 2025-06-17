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
                "content": '''
Ты - парсер напоминаний. Извлекай дату, время и текст. Отвечай строго в формате JSON, например: {\n\n'action': 'add',\n\n'text': 'забрать дочку из садика', \n\n'category': 'meeting',\n\n'address': 'Россия, Томская обл., Томск, ул. Вершинина, 39А',\n\n'datetime': '2023-11-20 09:40',\n\n'done': false,\n\n'condition': 'time'\n\n}.

Поля:
action - принимает значения add / delete / delete_all / update / show / error
text - если текст напоминания отсутствует, то action должен быть равен error, а текст равен пустой строке
category - принимает значения в контексте напоминания (на русском), например: покупки, дела, праздник и т.п.
address - принимает значение формального адреса, если адрес не указан, то равен пустой строке. Также если адрес указан не очень понятно, то всё равно пытайся указать формальный адрес (главное, чтобы адрес был однозначный, полный и реальный, в формате Страна, Область, Город, Улица, Дом)
datetime - принимает время напоминания. Если время и локация не указаны, то время принимает значение через час от текущего. Если указана локация и не указано время, то равно пустой строке.
done - всегда принимает значение False
condition - принимает значение time, если напоминание должно сработать по времени, иначе place
''' + f" Текущая дата: {current_datetime}"
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