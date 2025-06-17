import os
import speech_recognition as sr
from pydub import AudioSegment
from decription.text import parse_reminder_huggingface 

def ogg_to_text_google(filename):
    sound = AudioSegment.from_ogg(filename)
    wav_filename = "temp.wav"
    sound.export(wav_filename, format="wav", parameters=["-ac", "1", "-ar", "16000"])  # моно, 16 kHz

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
    try:
        transcription = ogg_to_text_google(audio_file_path)
        if not transcription:
            raise ValueError("Не удалось распознать текст из аудио")

        return parse_reminder_huggingface(transcription)

    except Exception as e:
        raise Exception(f"Ошибка обработки аудио: {str(e)}")