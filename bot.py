from asyncio import run, create_task
from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand, AllowedUpdates
from aiogram.utils.exceptions import MessageNotModified
import config
import handlers
from ls import tg_ls


storage = MemoryStorage()
bot = Bot(config.TG_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)


@dp.errors_handler(exception=MessageNotModified)
async def ignore_exception(update, exception):
    return True


async def on_startup():
    await bot.set_my_commands([
        BotCommand('kto', 'Команда которая преобразует введенное место и время в опрос. /format for more.'),
        BotCommand('weather', 'Погода на ближайшее время.'),
        BotCommand('all', 'Пинг всех участников конфы.'),
        # BotCommand('tmn', 'Пинг всех участников из Тюмени.'),
        # BotCommand('gamers', 'Пинг GAYмеров.'),
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
    handlers.register_all(dp)
    tg_ls.setup(dp)


async def main():
    register()
    await on_startup()
    try:
        await dp.skip_updates()
        await dp.start_polling(allowed_updates=AllowedUpdates.all())
    finally:
        await on_shutdown()


if __name__ == '__main__':
    run(main())
