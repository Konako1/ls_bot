from asyncio import run
from datetime import datetime

from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.utils.exceptions import MessageNotModified

import handlers
import open_ai.handle
from database import migrations, db
from handlers import weather
from modeus.modeus_middleware import ModeusMiddleware
from modeus.modeus_api import ModeusApi
from secret_chat import ls_group, config, test_group
from ls import tg_ls, pings, schedule, seven_tv, replicate_model

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
        BotCommand('help', 'Помогите'),
        BotCommand('anek', 'Рандомный анек с АКБ.'),
        BotCommand('format', 'Формат голосования.'),
        BotCommand('stop_poll', 'Остановить опрос.'),
        BotCommand('next', 'Показать следующую пару.'),
        BotCommand('day', 'Показать пары на день (+7).'),
        BotCommand('fc_toggle', 'Убрать/включить физру в выдачу.'),
        BotCommand('save_modeus_fio', 'Прикрепить ФИО к акку.'),
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


async def setup_middlewares():
    # modeus middleware
    modeus_api = ModeusApi()
    await modeus_api.endless_token_updater()
    dp.middleware.setup(ModeusMiddleware(modeus_api))


def register():
    schedule.setup(dp)
    handlers.register_all(dp)
    open_ai.handle.setup(dp)
    tg_ls.setup(dp)
    test_group.setup(dp)
    seven_tv.setup(dp)
    replicate_model.setup(dp)
    pings.setup(dp)

    ls_group.setup(dp)


async def main():
    register()
    await migrations.migrate(db.connection)
    await setup_middlewares()
    if datetime.now().hour == 8 or datetime.now().hour == 7:
        await bot.send_message(text=await weather.get_weather_message('Tyumen'), chat_id=config.ls_group_id)
    #    create_task(traveling_days.now_playing_checker(bot, 5))
    await on_startup()
    try:
        await dp.skip_updates()
        await dp.start_polling()
    finally:
        await on_shutdown()


if __name__ == '__main__':
    run(main())
