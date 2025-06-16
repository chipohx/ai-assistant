
# Первичная настройка - - - - - - - - - - - - - - - - - - - - - - - - -

import storage
import setup    # Настройка бота

# Определение всех сценариев  - - - - - - - - - - - - - - - - - - - - -

import state_handlers.greetings
import state_handlers.choose_event
import state_handlers.view_event_data
import state_handlers.edit_data
import state_handlers.setup_end

# Запуск работы бота - - - - - - - - - - - - - - - - - - - - - -  - - -

bot = storage.get_value('bot')
bot.polling(none_stop=True, interval=0)