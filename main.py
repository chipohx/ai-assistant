from loguru import logger
logger.info("Starting bot...")

# Первичная настройка - - - - - - - - - - - - - - - - - - - - - - - - -

import storage
import setup    # Настройка бота

# Определение всех сценариев  - - - - - - - - - - - - - - - - - - - - -

import state_handlers.greetings
import state_handlers.choose_event
import state_handlers.view_event_data
import state_handlers.edit_data
import state_handlers.setup_end
import state_handlers.idle
import state_handlers.reserve_handler # Он обязательно должен быть в конце, чтобы не мешать другим обработчикам

# Запуск работы бота - - - - - - - - - - - - - - - - - - - - - -  - - -

logger.info("Bot started successfully!")

bot = storage.get_value('bot')
bot.polling(none_stop=True, interval=0)