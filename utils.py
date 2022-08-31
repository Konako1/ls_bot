import re
from typing import Union

from aiogram import Bot
from aiogram.types import Message
from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageCantBeDeleted
from asyncio import sleep

from database import Db


class StickerFilter:
    def __init__(self, sticker_id: str, **kwargs):
        self._sticker_id = sticker_id
        self._kwargs = kwargs

    def __call__(self, message: Message) -> Union[dict, bool]:
        if message.sticker is None:
            return False
        # print(message.sticker.file_unique_id)
        if message.sticker.file_unique_id == self._sticker_id:
            return self._kwargs or True
        return False


def nice_pfp_filter(message: Message) -> Union[dict, bool]:
    if message.text is None:
        return False
    text = re.split(r'[,.;:\s]', message.text.lower())

    is_nice_in_text = 'найс' in text or 'nice' in text
    is_ava_in_text = 'ава' in text or 'ava' in text
    if not (is_nice_in_text and is_ava_in_text):
        return False

    return {'words': text}


async def message_sender(text_to_print: str, chat_id: int, bot: Bot, reply_markup=None):
    await bot.send_message(text=text_to_print, chat_id=chat_id, disable_web_page_preview=True, reply_markup=reply_markup)


async def is_anek_to_save(message: Message) -> bool:
    async with Db() as db:
        is_to_save = await db.get_is_message_to_save(message.message_id, message.chat.id)
        if is_to_save is None:
            print('message is not in DB wtf')
            raise Exception
        return is_to_save


async def delayed_delete(message: Message, sec: int, is_anek: bool = False):
    await sleep(sec)
    if is_anek and await is_anek_to_save(message):
        return
    try:
        await message.delete()
    except MessageToDeleteNotFound as e:
        await message.answer(text=f'Какой то ебалай удалил {message.text!r}, потому лови {e} себе в ебальник')
    except MessageCantBeDeleted as e:
        await message.answer(text=f'Я не ебу че произошло, но я не могу чето там удалить, а конкретно: {message.text}')