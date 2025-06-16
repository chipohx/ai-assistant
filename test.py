import requests
from datetime import datetime
import json
import re

# Ваш IAM-токен из Yandex Cloud
IAM_TOKEN = 't1.9euelZqblYmdl5OOjY6aypeTipnNye3rnpWaz5KVmYucz5vIip2Jns6Sj8bl9PdSE0E9-e9LPyvm3fT3TgxBPfnvSz8r5tXl9e-GnNGQnoqLl9GckJGMkJOa7fmQj5qRlpvN5_XrnpWakpfKk8qTjpXHzpCLlseXkY3v_M3X9dvPxpmam82ez9KZnsia0svGzZ7Sx57JxtKcnp6ZzpzHmsiZzMjv_sXrnpWakpfKk8qTjpXHzpCLlseXkY29656VmomampbKnZfPjpyXzJSczI6bteuelZrPkpWZi5zPm8iKnYmezpKPxg.CQH3YzDldh9FE_TvMAKrmJYY8yJvH_2w0sfKz8EpkWA2N1ANB5e6GVaCLdMK4A_hQXI7RITIikKo0IQtp9lSAg  '
FOLDER_ID = "b1gmdnrpom6eg5vk6o9g"


def parse_reminder_yandexgpt(text):
    current_datetime = datetime.now()
    print(current_datetime)
    headers = {
        "Authorization": f"Bearer {IAM_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 2000
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты парсер напоминаний. Извлекай дату, время и текст. Отвечай строго в JSON-формате, например: {\n\n'action': 'add',\n\n'text': 'забрать дочку из садика', \n\n'category': 'meeting',\n\n'location': '[37.617494, 55.752121]',\n\n'datetime': '2023-11-20 09:40',\n\n'done': false,\n\n'condition': 'time'\n\n}. Не добавляй никаких пояснений, только JSON. Action может быть add, delete и update. Condition может быть time (напоминание по времени), place (напоминание по месту) и timeplace (напоминание по времени и месту). Категории: meeting, shopping, holiday, business." + f" Текущая дата: {current_datetime}"
            },
            {
                "role": "user",
                "text": text
            }
        ]
    }

    response = requests.post(
        "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
        headers=headers,
        json=data,
    )

    if response.status_code == 200:
        result = response.json()["result"]["alternatives"][0]["message"]["text"]
        # print("Ответ модели:", result)  # Для отладки

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


# Пример использования
try:
    reminder = "Создай заметку на послезавтра на 6 часов вечера забрать дочку из садика горд Томск Главный корпус ТПУ"
    parsed_data = parse_reminder_yandexgpt(reminder)

    print(parsed_data)
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
    print(f"В ответе отсутствует ожидаемый ключ: {e}. Полный ответ: {parsed_data}")
except Exception as e:
    print(f"Произошла ошибка: {str(e)}")