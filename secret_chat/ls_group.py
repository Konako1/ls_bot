from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.filters import Text
from secret_chat.config import users, ls_group_id
from datetime import datetime
from secret_chat.frames import Frames
from secret_chat.simple_math import Calls

import re
import random


saved_messages = []


def id_converter(tg_id: list, name: str) -> str:
    return f'<a href="tg://user?id={tg_id}">{name}</a> '


async def delete_message(message: Message):
    await message.reply_to_message.delete()
    await message.delete()


async def nice_ava_checker(text: list[str]) -> bool:
    is_nice_in_text = False
    is_ava_in_text = False

    if 'ава' in text or 'ava' in text:
        is_ava_in_text = True

    if 'найс' in text or 'nice' in text:
        is_nice_in_text = True

    return is_nice_in_text and is_ava_in_text


async def nice_pfp(message: Message):
    calls = Calls()
    frames = Frames()
    text = re.split(r'[,.;:\s]', message.text.lower())
    print(text)

    if not await nice_ava_checker(text):
        return

    date_time = frames.get_datetime()
    msg_date = message.date
    if msg_date.hour == date_time.hour and msg_date.day == date_time.day:
        await message.reply("Сказать что ава моего хозяина ахуенная (или нет) можно всего раз в час.")
        return

    frames.set_datetime(msg_date)

    if 'не' in text:
        await message.bot.send_message(ls_group_id, ':(')
        return False

    await message.bot.send_message(ls_group_id, 'спс')

    calls.nice_pfp_sayed()
    info = await message.bot.get_chat(users['konako'])
    frame = info.bio.rsplit(" ", maxsplit=1)[1]
    frames.save_frame(int(frame))


async def test(message: Message):
    arg = message.text
    text = message_saver(arg)

    if text is None:
        return
    await message.reply(text=text)


def message_saver(text: str):
    arg = text

    if len(saved_messages) >= 4:
        saved_messages.pop(0)
    saved_messages.append(arg)

    return gde_tam_evkek()


def gde_tam_evkek():
    sabaka = "@konako1"
    names = ["ЕВЖЕЖЕЖКЖВЕЖЕВЖЫЫВАВАВЫЫЖЖЖЖЖ", "ежжеежжеежежжжеж", "ЖЪЖЪ", "евген", "евженя", "женя", "кот", "евжег", "евкек", "евгег"]
    where = ["живой", "жив", "где", "когда", "куда", "проснулся", "встал", "лег", "лежит",
             "спит", "уснул", "вышел", "пришел", "помылся", "моется", "помыл", "дома", "месте", "ткни", "пни", "толкни", ]

    is_sabaka = False
    is_name = False
    is_where = False

    for mes in saved_messages:  # type: str
        mes = re.sub(r"[\?!\.,\(\)]", "", mes)

        if sabaka in mes.lower():
            is_sabaka = True
        if any(name.lower() in mes.lower().split() for name in names):
            is_name = True
        if any(place in mes.lower().split() for place in where):
            is_where = True

    if is_sabaka and is_name and is_where:
        saved_messages.clear()
        rnd = random.randint(0, 5)
        message = ["Да не ебу я блять", "Я не знаю, хорошая моя", "Вообще идей 0",
                   "Я без понятия если честно", "Не ну тут хуй знает", "Ну не знаю я бляяяяяяять"]
        return message[rnd]
    else:
        return None


async def dishwasher_timer(bot: Bot):
    start_date = datetime.now()
    flag = False
    while True:
        if datetime.now().hour == start_date.hour:
            flag = False

        r = random.randint(0, 25)
        # print(r)
        if r == 0 and not flag:
            await message_sender('@evgfilim1, помой посуду плс', ls_group_id, bot)
            flag = True

        await asyncio.sleep(3600)


async def all(message: Message):
    chat_id = message.chat.id
    if chat_id < 0 and chat_id != -1001465546583:
        user_id = message.from_user.id
        await message.chat.unban(user_id)

    if chat_id > 0:
        await message.reply('И кого мне тут пинговать? Тебя?')
        return

    text = (id_converter(users["konako"], 'Величайший') +
            id_converter(users['evg'], 'Гегжег') +
            id_converter(users['gnome'], 'гном') +
            id_converter(users['yura'], 'Гоблин тинкер') +
            id_converter(users['lyoha'], 'Леха') +
            id_converter(users['acoola'], 'Акулятор') +
            id_converter(users['ship'], 'Корабль') +
            id_converter(users['gelya'], 'Сшсшсшгеля') +
            id_converter(users['bigdown'], 'BigDown') +
            id_converter(users['yana'], 'Яна') +
            id_converter(users['anastasia'], 'Анастэйша') +
            id_converter(users['smoosya'], 'гача-ремикс') +
            id_converter(users['sonya'], 'Вешалка'))
    await message.reply(
        text=text,
    )


async def tmn(message: Message):
    text = (id_converter(users["konako"], 'Величайший') +
            id_converter(users['evg'], 'Гегжег') +
            id_converter(users['gnome'], 'гном') +
            id_converter(users['lyoha'], 'Леха') +
            id_converter(users['acoola'], 'Акулятор') +
            id_converter(users['gelya'], 'Сшсшсшгеля') +
            id_converter(users['bigdown'], 'BigDown') +
            id_converter(users['yana'], 'Яна') +
            id_converter(users['anastasia'], 'Анастэйша') +
            id_converter(users['smoosya'], 'гача-ремикс'))
    await message.reply(
        text=text,
    )


async def gamers(message: Message):
    text = (id_converter(users['konako'], 'Cocknako') +
            id_converter(users['gnome'], 'гном') +
            id_converter(users['lyoha'], 'Льоха') +
            id_converter(users['evg'], 'Гегжук') +
            id_converter(users['yura'], 'Лошок') +
            id_converter(users['bigdown'], 'Богдан') +
            id_converter(users['ship'], 'Лодка') +
            id_converter(users['sonya'], 'Вешалка'))
    await message.reply(
        text=text,
    )


async def commands(message: Message):
    text = f'Список комманд:\n' \
           f'/кто - Команда которая преобразует введенное место и время в опрос. /format for more.\n' \
           f'/all - Пинг всех участников конфы.\n' \
           f'/tmn - Пинг всех участников из Тюмени.\n' \
           f'/gamers - Пинг GAYмеров.\n' \
           f'/pasta - Рандомная паста.\n' \
           f'/say - Бесполезная матеша.\n' \
           f'/graveyard - Количество голубей на кладбище.\n' \
           f'/update_top1 [nickname] [ss.sss] - Обновляет рекорд на Spring 05.\n' \
           f'/get_top1 - Возвращает топ 1 на Spring 05.\n' \
           f'Фичи:\n' \
           f'Словосочетания "голубь сдох" или "минус голубь" добавят одного голубя на кладбище.\n' \
           f'С некоторым шансом бот может кинуть медведя во время спама медведей.'

    await message.answer(
        text=text,
    )


# TODO: add hpb to schedule
# async def happy_birthday(_):
# aps.add_job()


# TODO: random bad apple video


def setup(dp: Dispatcher):
    dp.register_message_handler(delete_message, user_id=users['konako'], commands=['del'], chat_id=ls_group_id)
    dp.register_message_handler(all, commands=['all'])
    dp.register_message_handler(tmn, commands=['tmn'], chat_id=ls_group_id)
    dp.register_message_handler(gamers, commands=['gamers'], chat_id=ls_group_id)
    dp.register_message_handler(nice_pfp, Text(contains='ава', ignore_case=True), chat_id=ls_group_id)
    dp.register_message_handler(nice_pfp, Text(contains='ava', ignore_case=True), chat_id=ls_group_id)
    dp.register_message_handler(test, user_id=users['acoola'], chat_id=ls_group_id)
    dp.register_message_handler(commands, commands=['commands'], chat_id=ls_group_id)
