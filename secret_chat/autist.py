from aiogram import Dispatcher
from aiogram.dispatcher.handler import SkipHandler
from aiogram.types import Message
from secret_chat.config import ls_group_id, test_group_id, users


async def autist(message: Message):
    if message.from_user.id != users['lyoha']:
        raise SkipHandler


def setup(dp: Dispatcher):
    dp.register_message_handler(autist, chat_id=ls_group_id)
