from ls import tg_ls
import vk_api
from secret_chat import ls_group, config, test_group
from asyncio import run
from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand


bot = Bot(config.TG_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)


async def on_startup():
    await bot.set_my_commands([
        BotCommand('kto', 'Команда которая преобразует введенное место и время в опрос. /format for more.'),
        BotCommand('say', 'Бесполезная матеша.'),
        BotCommand('pasta', 'Рандомная паста.'),
        BotCommand('graveyard', 'Количество голубей на кладбище.'),
        BotCommand('get_top1', 'Возвращает топ 1 на Spring 05.'),
        BotCommand('update_top1', '[nickname] [ss.sss] - Обновляет рекорд на Spring 05.'),
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
    await on_startup()
    try:
        await dp.skip_updates()
        await dp.start_polling()
    finally:
        await on_shutdown()


if __name__ == '__main__':
    run(main())
