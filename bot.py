from ls import tg_ls
import traveling_days
from secret_chat import ls_group, config, test_group
from asyncio import run, create_task
from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand, AllowedUpdates

bot = Bot(config.TG_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)


async def on_startup():
    await bot.set_my_commands([
        BotCommand('kto', 'Команда которая преобразует введенное место и время в опрос. /format for more.'),
        BotCommand('say', 'Бесполезная матеша.'),
        BotCommand('pasta', 'Рандомная паста.'),
        BotCommand('graveyard', 'Количество голубей на кладбище.'),
        BotCommand('all', 'Пинг всех участников конфы.'),
        # BotCommand('tmn', 'Пинг всех участников из Тюмени.'),
        # BotCommand('gamers', 'Пинг GAYмеров.'),
        BotCommand('features', 'Фичи бота.'),
        BotCommand('anek', 'Рандомный анек с АКБ.'),
        BotCommand('format', 'Формат голосования.')
    ]
    )


async def on_shutdown():
    pass


def register():
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
