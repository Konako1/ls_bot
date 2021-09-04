import re
from typing import Union

from aiogram import Bot
from aiogram.types import Message
from aiogram.utils.exceptions import MessageToDeleteNotFound
from asyncio import sleep


class StickerFilter:
    def __init__(self, sticker_id: str, **kwargs):
        self._sticker_id = sticker_id
        self._kwargs = kwargs

    def __call__(self, message: Message) -> Union[dict, bool]:
        if message.sticker is None:
            return False
        # print(message.sticker.file_unique_id)
        if message.sticker.file_unique_id == self._sticker_id:
            return self._kwargs
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


async def message_sender(text_to_print: str, chat_id: int, bot: Bot):
    await bot.send_message(text=text_to_print, chat_id=chat_id, disable_web_page_preview=True)


async def delayed_delete(message: Message, sec: int):
    await sleep(sec)
    try:
        await message.delete()
    except MessageToDeleteNotFound as e:
        await message.answer(text=f'Какой то ебалай удалил сообщение, потому лови {e} себе в ебальник')
