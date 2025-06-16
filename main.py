from voice import parse_reminder_from_audio
from text import parse_reminder_huggingface
import os

if __name__ == "__main__":
    format = 'text' # заменить
    try:
        if format=='audio': # заменить
            audio_file = "said.ogg" # заменить
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"Аудио файл {audio_file} не найден")
            result = parse_reminder_from_audio(audio_file)
            print(f'audio {result}')
        elif format=='text': # заменить
            reminder = "Напомни мне завтра купить пиво" # заменить
            result = parse_reminder_huggingface(reminder)
            print(f'text {result}')

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")