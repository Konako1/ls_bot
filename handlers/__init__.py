from aiogram import Dispatcher

from . import kto, weather


def register_all(dp: Dispatcher):
    kto.register(dp)
    weather.register(dp)
