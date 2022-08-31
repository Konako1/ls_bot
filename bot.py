from asyncio import run
from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand, AllowedUpdates
from aiogram.utils.exceptions import MessageNotModified
import config
from ls import tg_ls


storage = MemoryStorage()
bot = Bot(config.TG_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)


@dp.errors_handler(exception=MessageNotModified)
async def ignore_exception(update, exception):
    return True


async def on_startup():
    await bot.set_my_commands([
        BotCommand('weather', 'Погода на ближайшее время.'),
    ]
    )


async def on_shutdown():
    pass


def register():
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
