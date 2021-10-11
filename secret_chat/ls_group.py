import asyncio
from typing import Optional

from aiogram import Dispatcher, Bot
from aiogram.types import Message, ContentTypes, InputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from secret_chat import mc_server
from secret_chat.config import users, ls_group_id, test_group_id, frames_dir
from datetime import datetime
from utils import StickerFilter, nice_pfp_filter, message_sender
from asyncio import create_task
from database import Db, StatType

import re
import random


saved_messages = []


def id_converter(tg_id: list, name: str) -> str:
    return f'<a href="tg://user?id={tg_id}">{name}</a> '


async def delete_message(message: Message):
    await message.reply_to_message.delete()
    await message.delete()


async def change_pfp(message: Message, words: Optional[list[str]] = None, is_nice: Optional[bool] = None) -> bool:
    if words is not None and 'не' in words or is_nice is False:
        await message.bot.send_message(ls_group_id, 'Сорян, реально говно какое-то поставил, исправляюсь.')
        await message.bot.send_message(test_group_id, 'NeNicePfp_FUCKING_ALERT1337')
        return True
    return False


async def add_pfp_in_db(message: Message, db: Db):
    info = await message.bot.get_chat(users['konako'])
    frame = info.bio.rsplit(" ", maxsplit=1)[1]
    await db.add_frame(int(frame), message.date.timestamp())
    await message.bot.send_message(ls_group_id, 'спс')
    await db.update_stat(StatType().nice_pfp)


async def nice_pfp(message: Message, words: Optional[list[str]] = None, is_nice: Optional[bool] = None):
    async with Db() as db:
        frame_data = await db.get_last_frame()
        if frame_data is None:
            if await change_pfp(message, words, is_nice):
                return
            await add_pfp_in_db(message, db)
            return

        date_time = datetime.fromtimestamp(frame_data.datetime)
        msg_date = message.date
        if msg_date.hour == date_time.hour and msg_date.day == date_time.day:
            await message.reply("Сказать что ава моего хозяина ахуенная (или нет) можно всего раз в час.")
            return

        if await change_pfp(message, words, is_nice):
            return

        await add_pfp_in_db(message, db)


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


async def get_pic_from_num(message: Message):
    args = message.get_args()
    try:
        pic = InputFile(f'{frames_dir}pic{args}.jpg')
        await message.reply_photo(pic)
    except FileNotFoundError:
        await message.reply(f'ты еблан, пиши /pic <code>[0 &lt;= num &lt; 5670]</code>', parse_mode='HTML')


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
async def be_bra(message: Message):
    be = ["бе", "бе.", "бе!", "бе?", "бе,"]
    if message.text.lower() in be and message.from_user.id == users['acoola']:
        await message.reply('бра')


async def server_status(message: Message):
    text = 'Статус сервера: '
    is_online = await mc_server.is_server_open()
    text += 'Online' if is_online else 'Offline'
    await message.reply(text)


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
            id_converter(users['sonya'], 'Вешалка') +
            id_converter(users['karina'], 'Новичьок'))
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
            id_converter(users['smoosya'], 'гача-ремикс') +
            id_converter(users['karina'], 'Новичьок'))
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


async def senat(message: Message):
    text = (
        id_converter(users['konako'], 'Цезарь') +
        id_converter(users['gnome'], 'Август') +
        id_converter(users['sonya'], 'Екатерина II') +
        id_converter(users['gelya'], 'Елизовета Петровна')
    )
    await message.reply(text)


async def commands(message: Message):
    text = f'Список комманд:\n' \
           f'/кто - Команда которая преобразует введенное место и время в опрос. /format for more.\n' \
           f'/all - Пинг всех участников конфы.\n' \
           f'/tmn - Пинг всех участников из Тюмени.\n' \
           f'/gamers - Пинг GAYмеров.\n' \
           f'/status - Статус майнкрафт сервера.\n' \
           f'/pasta - Рандомная паста.\n' \
           f'/say - Бесполезная матеша.\n' \
           f'/graveyard - Количество голубей на кладбище.\n' \
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
    dp.register_message_handler(nice_pfp, nice_pfp_filter, chat_id=ls_group_id)
    dp.register_message_handler(nice_pfp, StickerFilter('AgAD0xAAAh3DcUk', is_nice=True), content_types=ContentTypes.STICKER, chat_id=ls_group_id)
    dp.register_message_handler(nice_pfp, StickerFilter('AgAD-BQAAs57cEk', is_nice=False), content_types=ContentTypes.STICKER, chat_id=ls_group_id)
    dp.register_message_handler(nice_pfp, StickerFilter('AgAD-hEAAuepaUk', is_nice=False), content_types=ContentTypes.STICKER, chat_id=ls_group_id)
    dp.register_message_handler(test, user_id=users['acoola'], chat_id=ls_group_id)
    dp.register_message_handler(commands, commands=['commands', 'c'], chat_id=ls_group_id)
    dp.register_message_handler(get_pic_from_num, commands=['pic'], chat_id=[test_group_id, ls_group_id])
    dp.register_callback_query_handler(callback_handler, text=['yes', 'no'], chat_id=test_group_id)
    dp.register_message_handler(be_bra, regexp=re.compile(r'\bбе\b', re.I), chat_id=ls_group_id)
    dp.register_message_handler(server_status, commands='status', chat_id=ls_group_id)
