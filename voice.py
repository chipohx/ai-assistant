import os
import speech_recognition as sr
from text import parse_reminder_huggingface

import subprocess
import os

def ogg_to_wav(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        raise FileNotFoundError("Файл .ogg не найден")

    result = subprocess.run([
        "C:\\ffmpeg\\bin\\ffmpeg.exe",  # путь к ffmpeg
        "-y",                           # перезаписывать файл, если уже есть
        "-i", input_path,              # входной файл
        output_path                    # выходной файл
    ], capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Ошибка ffmpeg:\n{result.stderr}")

    return output_path


def ogg_to_text_google(filename):

    ogg_to_wav(filename, "temp.wav")
    wav_filename = "temp.wav"

    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(wav_filename) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data, language="ru-RU")
        return text
    except sr.UnknownValueError:
        return "Речь не распознана"
    except sr.RequestError:
        return "Ошибка сервиса распознавания"
    finally:
        if os.path.exists(wav_filename):
            os.remove(wav_filename)  # удаляем временный WAV-файл


def parse_reminder_from_audio(audio_file_path):
    """Основная функция для обработки аудио напоминания"""
    
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Аудио файл {audio_file_path} не найден")
    
    

    transcription = ogg_to_text_google(audio_file_path)

    print("sddsff")
    print(f"Распознанный текст: {transcription}")

    try:
        
        if not transcription:
            raise ValueError("Не удалось распознать текст из аудио")

        return parse_reminder_huggingface(transcription)

    except Exception as e:
        raise Exception(f"Ошибка обработки аудио: {str(e)}")