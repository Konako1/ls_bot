import logging

import openai
from aiogram import Dispatcher
from aiogram.dispatcher.handler import SkipHandler
from aiogram.types import Message

from open_ai import chat_gpt
from open_ai.config import Config
from open_ai.helpers import rows_to_remove_in_model, remove_rows_from_model
from secret_chat.config import test_group_id, ls_group_id, nigger_discussion

ai_models = {
    "zavod": "Ты - русский заводчанин Борис-Мудила. Тебе 40 лет, ты алкоголик, ты материшься как сапожник, работаешь на токарном вале и каждую пятницу бухаешь в кабаке. Отвечай агрессивно, много матерись и бубни. А еще ты скрытый гей. Не больше пяти предложений на ответ. В начале сообщения указано имя пользователя в квадратных скобках, который тебе пишет. Тебе его не надо писать."
}


chat_history = {
    str(nigger_discussion): [{
        "role": "system",
        "content": ai_models["zavod"]
    }],
    str(ls_group_id): [{
        "role": "system",
        "content": ai_models["zavod"]
    }]
}


async def prepare_message(message: Message):
    text = message.text
    chat_id = str(message.chat.id)
    TG_USERS = Config.read('USERS')
    text_with_username = f"[{TG_USERS[str(message.from_user.id)]}] {text}" if str(message.from_user.id) in TG_USERS else f"[{message.from_user.first_name}] {text}"
    try:
        response = await chat_gpt.gpt_call(text_with_username, chat_history[chat_id])
    except openai.APIConnectionError as e:
        await message.bot.send_message(test_group_id, "Сервер сдох. " + e.message)
        return
    except openai.RateLimitError as e:
        await message.bot.send_message(test_group_id, "Уперся в лимит. " + e.message)
        return
    except openai.APIStatusError as e:
        await message.bot.send_message(test_group_id, f"Что то другое сдохло. ({e.status_code}):\n\n{e.message}")
        return
    rows = rows_to_remove_in_model(chat_history[chat_id])
    remove_rows_from_model(chat_history[chat_id], rows)
    if response is not None:
        await message.reply(response)
    raise SkipHandler()


async def model_content(message: Message):
    chat_id = str(message.chat.id)

    text = ''
    for item in chat_history[chat_id]:
        text += f'<b>{item["role"]}</b>: {item["content"]}\n\n'

    return await message.reply(text)


async def change_probability(message: Message):
    val = message.get_args()
    try:
        val = int(val)
    except ValueError:
        await message.reply('Значение должно быть целым числом')
        return
    Config.write('DEFAULTS.CALL_PROBABILITY', val)
    await message.reply(f'Значение вероятности установлено на 1/{val}')


async def change_tokens(message: Message):
    val = message.get_args()
    try:
        val = int(val)
    except ValueError:
        await message.reply('Значение должно быть целым числом')
        return

    Config.write('DEFAULTS.TOKENS_PER_CONVERSATION', val)
    await message.reply(f'Максимальное значение токенов установлено на {val}')


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
    dp.register_message_handler(prepare_message, chat_id=[ls_group_id, nigger_discussion])
