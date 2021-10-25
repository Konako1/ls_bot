from aiogram import Dispatcher

from . import kto


def register_all(dp: Dispatcher):
    kto.register(dp)
