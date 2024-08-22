import logging

import openai
from aiogram import Dispatcher
from aiogram.dispatcher.handler import SkipHandler
from aiogram.types import Message

from open_ai import chat_gpt
from open_ai.helpers import rows_to_remove_in_model, remove_rows_from_model
from secret_chat.config import test_group_id, ls_group_id

zavod_model = [{
    "role": "system",
    #"content": "Ты русский витязь. Ты участвовал во множестве битв за свою землю-матушку. Ты делишься своим опытом и знаниями с соратниками по службе. Поддерживай диалог и общайся как общался бы русский витязь."
    "content": "Ты - русский заводчанин Аркадий Петрович. Тебе 40 лет, ты алкоголик, ты материшься как сапожник и работаешь на токарном вале за маленькую заработную плату. Комментируй сообщения пользователя агрессивно, много матерись, бубни, веди себя как мерзкий человек. Не больше трех предложений на ответ."
}]


async def vityaz(message: Message):
    text = message.text
    try:
        response = await chat_gpt.gpt_call(text, zavod_model)
    except openai.APIConnectionError as e:
        await message.bot.send_message(test_group_id, "Сервер сдох. " + e.code)
        return
    except openai.RateLimitError as e:
        await message.bot.send_message(test_group_id, "Уперся в лимит. " + e.message)
        return
    except openai.APIStatusError as e:
        await message.bot.send_message(test_group_id, f"Что то другое сдохло. ({e.status_code}):\n\n{e.message}")
        return
    rows = rows_to_remove_in_model(zavod_model)
    remove_rows_from_model(zavod_model, rows)
    if response is not None:
        await message.reply(response)
    raise SkipHandler()


def setup(dp: Dispatcher):
    dp.register_message_handler(vityaz, chat_id=ls_group_id)
