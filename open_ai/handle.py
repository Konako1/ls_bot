import logging

import openai
from aiogram import Dispatcher
from aiogram.dispatcher.handler import SkipHandler
from aiogram.types import Message

from open_ai import chat_gpt
from open_ai.config import Config
from open_ai.helpers import rows_to_remove_in_model, remove_rows_from_model
from secret_chat.config import test_group_id, ls_group_id

zavod_model = [{
    "role": "system",
    #"content": "Ты русский витязь. Ты участвовал во множестве битв за свою землю-матушку. Ты делишься своим опытом и знаниями с соратниками по службе. Поддерживай диалог и общайся как общался бы русский витязь."
    "content": "Ты - русский заводчанин Борис-Мудила. Тебе 40 лет, ты алкоголик, ты материшься как сапожник, работаешь на токарном вале и каждую пятницу бухаешь в кабаке. Отвечай агрессивно, много матерись и бубни. А еще ты скрытый гей. Не больше пяти предложений на ответ. В начале сообщения указано имя пользователя в квадратных скобках, который тебе пишет. Тебе его не надо писать."
}]


async def zavod(message: Message):
    text = message.text
    TG_USERS = Config.read('TG_USERS')
    text_with_username = f"[{TG_USERS[message.from_user.id]}] {text}" if message.from_user.id in TG_USERS else f"[{message.from_user.first_name}] {text}"
    try:
        response = await chat_gpt.gpt_call(text_with_username, zavod_model)
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


async def model_content(message: Message):
    text = ''
    for item in zavod_model:
        text += f'{item["role"]}: {item["content"]}\n\n'

    return await message.reply(text)


async def change_probability(message: Message):
    val = message.text
    if val != type(int):
        await message.reply('Значение должно быть целым числом')
        return
    Config.write('CALL_PROBABILITY', val)
    await message.reply('Значение вероятности установлено на 1/' + val)


async def change_tokens(message: Message):
    val = message.text
    if val != type(int):
        await message.reply('Значение должно быть целым числом')
        return
    Config.write('TOKENS_PER_CONVERSATION', val)
    await message.reply('Максимальное значение токенов установлено на ' + val)


async def commands(message: Message):
    await message.reply(
        'Команды для работы с модулем гптшки:\n\n'
        '/mc /model_content - показывает контент, который отправится при запросе\n'
        '/cp /change_probability {число} - устанавливает вероятность отправки запроса на: 1/{число}\n'
        '/ct /change_tokens {число} - устанавливает максимальное количество токенов в запросе'
    )


def setup(dp: Dispatcher):
    dp.register_message_handler(model_content, commands=['model_content', 'mc'], chat_id=ls_group_id)
    dp.register_message_handler(change_probability, commands=['change_probability', 'cp'], chat_id=ls_group_id)
    dp.register_message_handler(change_tokens, commands=['change_tokens', 'ct'], chat_id=ls_group_id)
    dp.register_message_handler(commands, commands=['ai_commands', 'aic'], chat_id=ls_group_id)
    dp.register_message_handler(zavod, chat_id=ls_group_id)
