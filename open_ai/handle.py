import openai
from aiogram import Dispatcher
from aiogram.dispatcher.handler import SkipHandler
from aiogram.types import Message

from open_ai import chat_gpt
from secret_chat.config import test_group_id


async def vityaz(message: Message):
    text = message.text
    print(text)
    try:
        response = await chat_gpt.gpt_call(text)
    except openai.APIConnectionError as e:
        await message.reply("The server could not be reached")
        return
    except openai.RateLimitError as e:
        await message.reply("A 429 status code was received; we should back off a bit.")
        return
    except openai.APIStatusError as e:
        await message.reply(f"Another non-200-range status code was received ({e.status_code}):\n\n{e.message}")
        return
    await message.reply(response)
    raise SkipHandler()


def setup(dp: Dispatcher):
    dp.register_message_handler(vityaz, chat_id=test_group_id)
