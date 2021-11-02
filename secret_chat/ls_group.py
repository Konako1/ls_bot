import asyncio
from collections import Callable
from re import Match
from typing import Optional

from aiogram import Dispatcher, Bot
from aiogram.types import Message, ContentTypes, InputFile, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery, ChatMemberUpdated

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
    if words is not None and ('не' in words or 'not' in words) or is_nice is False:
        await message.bot.send_message(ls_group_id, 'Сорян, реально говно какое-то поставил, исправляюсь.')
        await message.bot.send_message(test_group_id, 'NeNicePfp_FUCKING_ALERT1337')
        return True
    return False


async def get_frame_from_bio(message: Message) -> int:
    info = await message.bot.get_chat(users['konako'])
    frame = info.bio.rsplit(" ", maxsplit=1)[1]
    return int(frame)


async def add_pfp_in_db(message: Message, db: Db):
    frame = await get_frame_from_bio(message)
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
            await message.reply("Сказать что ава моего хозяина ахуенная можно всего раз в час.")
            return

        if await change_pfp(message, words, is_nice):
            return

        await add_pfp_in_db(message, db)


async def nice_pfp_rollback(message: Message):
    frame = await get_frame_from_bio(message)
    async with Db() as db:
        answer = await db.remove_frame(frame)
        if answer is None:
            await message.reply('Такой фрейм еще не был сохранен')
        if answer:
            await message.reply('Удалено')


async def simp_moment(message: Message):
    await message.answer('@evgfilim1 @s1rius9')


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


async def timecode(message: Message):
    text = message.text
    if '?t=' in text:
        await message.answer('( таймкод на месте )')


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


def somebody_left(event: ChatMemberUpdated):
    return event.old_chat_member.status not in ("left", "kicked") \
           and event.new_chat_member.status in ("left", "kicked") \
           and not event.new_chat_member.user.is_bot


def somebody_joined(event: ChatMemberUpdated):
    return event.new_chat_member.status not in ("left", "kicked") \
           and event.old_chat_member.status in ("left", "kicked") \
           and not event.new_chat_member.user.is_bot


def re_increment(match: Match[str]) -> str:
    return str(int(match[1]) + 1)


def re_decrement(match: Match[str]) -> str:
    return str(int(match[1]) - 1)


def get_new_title(old_title: str, sub_func: Callable[[Match[str]], str]) -> str:
    if (new_title := re.sub(r"(\d+)", sub_func, old_title)) != old_title:  # anything changed
        return new_title
    raise ValueError


async def novichok(event: ChatMemberUpdated):
    try:
        await event.bot.set_chat_title(event.chat.id, get_new_title(event.chat.title, re_increment))
    except ValueError:
        await event.bot.send_message(
            event.chat.id,
            "Кто-то зашёл в чат, но цифр в названии чата я не нашёл, поэтому хуй там я поменяю"
            " вам название, ебитесь сами"
        )


async def uzhe_smesharik(event: ChatMemberUpdated):
    try:
        await event.bot.set_chat_title(event.chat.id, get_new_title(event.chat.title, re_decrement))
    except ValueError:
        await event.bot.send_message(
            event.chat.id,
            "Кто-то вышел из чата, но цифр в названии чата я не нашёл, поэтому хуй там я поменяю"
            " вам название, ебитесь сами"
        )


def setup(dp: Dispatcher):
    dp.register_message_handler(delete_message, user_id=users['konako'], commands=['del'], chat_id=ls_group_id)
    dp.register_message_handler(all, commands=['all'])
    dp.register_message_handler(tmn, commands=['tmn'], chat_id=ls_group_id)
    dp.register_message_handler(gamers, commands=['gamers'], chat_id=ls_group_id)
    dp.register_message_handler(senat, commands=['senat'], chat_id=ls_group_id)
    dp.register_message_handler(timecode, regexp=re.compile(r'https://youtu\.be/', re.I), chat_id=ls_group_id)
    dp.register_message_handler(nice_pfp, nice_pfp_filter, chat_id=ls_group_id)
    dp.register_message_handler(nice_pfp, StickerFilter('AgAD0xAAAh3DcUk', is_nice=True), content_types=ContentTypes.STICKER, chat_id=ls_group_id)
    dp.register_message_handler(nice_pfp, StickerFilter('AgAD-BQAAs57cEk', is_nice=False), content_types=ContentTypes.STICKER, chat_id=ls_group_id)
    dp.register_message_handler(nice_pfp, StickerFilter('AgAD-hEAAuepaUk', is_nice=False), content_types=ContentTypes.STICKER, chat_id=ls_group_id)
    dp.register_message_handler(simp_moment, StickerFilter('AgADxhQAAvm9AUs'), content_types=ContentTypes.STICKER, chat_id=ls_group_id)
    dp.register_message_handler(test, user_id=users['acoola'], chat_id=ls_group_id)
    dp.register_message_handler(commands, commands=['commands', 'c'], chat_id=ls_group_id)
    dp.register_message_handler(get_pic_from_num, commands=['pic'], chat_id=[test_group_id, ls_group_id])
    dp.register_message_handler(nice_pfp_rollback, commands=['rollback'], chat_id=ls_group_id, user_id=users['konako'])
    dp.register_message_handler(be_bra, regexp=re.compile(r'\bбе\b', re.I), chat_id=ls_group_id)
    dp.register_message_handler(server_status, commands='status', chat_id=ls_group_id)

    dp.register_chat_member_handler(novichok, somebody_joined, chat_id=ls_group_id)
    dp.register_chat_member_handler(uzhe_smesharik, somebody_left, chat_id=ls_group_id)
