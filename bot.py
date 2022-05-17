from asyncio import run, create_task
from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand, AllowedUpdates
from aiogram.utils.exceptions import MessageNotModified

import traveling_days
import handlers
from ls import tg_ls
from secret_chat import ls_group, config, test_group, autist


storage = MemoryStorage()
bot = Bot(config.TG_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)


@dp.errors_handler(exception=MessageNotModified)
async def ignore_exception(update, exception):
    return True


async def on_startup():
    await bot.set_my_commands([
        BotCommand('kto', 'Команда которая преобразует введенное место и время в опрос. /format for more.'),
        BotCommand('say', 'Бесполезная матеша.'),
        BotCommand('weather', 'Погода на ближайшее время.'),
        BotCommand('pasta', 'Рандомная паста.'),
        BotCommand('graveyard', 'Количество голубей на кладбище.'),
        BotCommand('all', 'Пинг всех участников конфы.'),
        # BotCommand('tmn', 'Пинг всех участников из Тюмени.'),
        # BotCommand('gamers', 'Пинг GAYмеров.'),
        BotCommand('features', 'Фичи бота.'),
        BotCommand('anek', 'Рандомный анек с АКБ.'),
        BotCommand('format', 'Формат голосования.'),
        BotCommand('stop_poll', 'Остановить опрос.'),
        BotCommand('create_ping_command', 'Создать команду для пинга участников в чате.'),
        BotCommand('delete_ping_command', 'Удалить уже созданную команду.'),
        BotCommand('add_me', 'Добавить себя в команду для пинга.'),
        BotCommand('delete_me', 'Удалить себя из команды для пинга.'),
        BotCommand('ping_commands', 'Показать все доступные в чате команды.'),
        BotCommand('my_commands', 'Показать все доступные мне команды.'),
    ]
    )


async def on_shutdown():
    pass


def register():
    # autist.setup(dp)
    handlers.register_all(dp)
    tg_ls.setup(dp)
    test_group.setup(dp)
    ls_group.setup(dp)


async def main():
    register()
    create_task(ls_group.dishwasher_timer(bot))
    create_task(traveling_days.now_playing_checker(bot, 5))
    await on_startup()
    try:
        await dp.skip_updates()
        await dp.start_polling(allowed_updates=AllowedUpdates.all())
    finally:
        await on_shutdown()


if __name__ == '__main__':
    run(main())
