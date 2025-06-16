import os
import requests
import json
import re
from datetime import datetime

# Конфигурация API
HF_API_TOKEN = "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"
WHISPER_MODEL = "openai/whisper-large-v3"
LLM_MODEL = "deepseek/deepseek-v3-0324"


def transcribe_audio(audio_path):
    """Транскрибирует аудио через Whisper API"""
    with open(audio_path, "rb") as f:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{WHISPER_MODEL}",
            headers={"Authorization": f"Bearer {HF_API_TOKEN}", "content-type": "audio/ogg"},
            data=f
        )

    if response.status_code != 200:
        raise Exception(f"Ошибка транскрипции: {response.status_code} - {response.text}")

    return response.json().get("text", "")


def parse_reminder(text, current_date):
    """Анализирует текст напоминания через LLM"""
    prompt = f"""
    Ты парсер напоминаний. Извлеки данные в JSON:
    {{
        "action": "add|delete|update",
        "text": "текст напоминания",
        "category": "meeting|shopping|holiday|business",
        "address": "адрес (если есть)",
        "datetime": "YYYY-MM-DD HH:MM",
        "done": false,
        "condition": "time|place|timeplace"
    }}
    Текущая дата: {current_date}
    Текст: "{text}"
    """

    response = requests.post(
        f"https://api-inference.huggingface.co/models/{LLM_MODEL}",
        headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
        json={"inputs": prompt}
    )

    if response.status_code != 200:
        raise Exception(f"Ошибка LLM: {response.status_code} - {response.text}")

    return extract_json_from_response(response.json())


def extract_json_from_response(response_data):
    """Извлекает JSON из ответа модели"""
    if isinstance(response_data, list):
        response_data = response_data[0]

    if isinstance(response_data, dict):
        return response_data

    if isinstance(response_data, str):
        match = re.search(r'\{.*\}', response_data, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

    raise ValueError("Не удалось извлечь JSON из ответа")


def parse_reminder_from_audio(audio_path):
    """Основная функция обработки аудио"""
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Аудио файл не найден: {audio_path}")

    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Транскрипция аудио
    transcription = transcribe_audio(audio_path)
    if not transcription:
        raise ValueError("Не удалось распознать текст в аудио")

    # 2. Анализ напоминания
    return parse_reminder(transcription, current_date)


# Пример использования
if __name__ == "__main__":
    try:
        result = parse_reminder_from_audio("said.ogg")
        print("Результат:", json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Ошибка: {str(e)}")