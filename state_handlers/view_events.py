from loguru import logger
logger.info("Adding view event data state handler...")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


from telebot import types
import storage

bot = storage.get_value('bot')

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
PAGE_SIZE = 5

def show_events(chat_id):
    session_id = chat_id
    
    sessions = storage.get_value('sessions')
    if not sessions:
        sessions = {}
        sessions[session_id] = {}

    if 'event_list' not in sessions[session_id]:
        sessions[session_id]['event_list'] = []

    _send_page(chat_id, sessions[session_id]['event_list'], session_id, page=0)


def _send_page(chat_id, event_list, session_id, page, message_id=None):
    total_pages = (len(event_list) - 1) // PAGE_SIZE + 1
    page = max(0, min(page, total_pages - 1))
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    events = event_list[start:end]

    # Текст
    if not events:
        text = "❌ Напоминания не найдены."
    else:

        text = f"📄 Страница {page + 1} из {total_pages}\n\n"

        for i, e in enumerate(events, start=start):

            text += f"🔹 {i+1}. "
            text += f"{e['text'].capitalize()}\n"
            text += f"Время: {e['datetime'][:16].replace('T',' ')}\n" if e["condition"] == "time" else f"Место: {e['address']}\n"
            text += f"Тип: {e['category']}\n\n"

    # Кнопки: выбрать и листать
    markup = types.InlineKeyboardMarkup(row_width=2)

    for i in range(start, min(end, len(event_list))):
        markup.add(types.InlineKeyboardButton(
            text=f"📌 Выбрать {i + 1}",
            callback_data=f"select:{i}"
        ))

    # Клавиатура

    if page > 0:
        markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page - 1}"))
    if page < total_pages - 1:
        markup.add(types.InlineKeyboardButton("➡️ Далее", callback_data=f"page_{page + 1}"))

    # Вывод
    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: '_' in call.data and call.data.startswith("page_"))
def handle_page_turn(call):
    session_id = int(call.message.chat.id)

    sessions = storage.get_value('sessions')

    if not sessions or session_id not in sessions:
        bot.answer_callback_query(call.id, "⛔ Сессия не найдена.")
        return

    page = int(call.data.split("_")[1])
    events = sessions[session_id]["event_list"]
    _send_page(call.message.chat.id, events, session_id, page, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)