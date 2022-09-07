import asyncio
import logging
from collections import Callable
from re import Match
from typing import Optional

from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.handler import SkipHandler
from aiogram.types import Message, ContentTypes, InputFile, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery, ChatMemberUpdated, ChatMemberAdministrator, ChatPermissions, ForceReply
from aiogram.utils.exceptions import CantRestrictChatOwner, UserIsAnAdministratorOfTheChat, CantRestrictSelf, BadRequest

from secret_chat import mc_server
from secret_chat.config import users, ls_group_id, test_group_id, frames_dir
from datetime import datetime
from utils import StickerFilter, nice_pfp_filter, message_sender, somebody_joined, somebody_left
from asyncio import create_task, sleep
from database import Db, StatType, SilenceInfo

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
        raise SkipHandler
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
    if any(item in message.text.lower() for item in be):
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


async def unsilence_delay(message: Message, sec: int):
    await asyncio.sleep(sec)
    await unsilence(message)


async def restrict_user(message: Message, user_id: int) -> bool:
    try:
        await message.chat.restrict(user_id, permissions=ChatPermissions(can_send_messages=False))
    except AttributeError as e:
        await message.reply('Реплайни сообщение, дебил')
        return False
    except CantRestrictChatOwner as e:
        await message.reply('Нельзя мутить создателя беседы')
        return False
    except UserIsAnAdministratorOfTheChat as e:
        await message.reply('Нельзя мутить админа беседы, которого промотил не бот')
        return False
    except CantRestrictSelf as e:
        await message.reply('Пошел нахуй.')
        return False
    return True


async def get_member_title(message: Message, user_id: int) -> str:
    member = await message.chat.get_member(user_id)
    if isinstance(member, ChatMemberAdministrator):
        title = member.custom_title
    else:
        title = ''
    return title


async def silence_info_check(user_id: int, title: str = None) -> SilenceInfo:
    async with Db() as db:
        silence_info = await db.get_user_silence_info(user_id)
        print(f'{repr(silence_info.title)} | {silence_info.is_silenced} | {repr(title)}')
        if title is None:
            title = silence_info.title
        if silence_info.is_silenced is None:
            await db.add_user_in_silences(user_id, 0, title)
            return SilenceInfo(None, None)
        return silence_info


async def set_custom_title(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    gender = 'ты'
    custom_title = message.get_args()
    if len(custom_title) > 16:
        await message.reply(f'Соси жопу, сильно дохуя')
        return
    if custom_title == '':
        custom_title = 'Admin'
    if message.reply_to_message is not None:
        user_id = message.reply_to_message.from_user.id
        gender = message.reply_to_message.from_user.username
    is_success = await message.bot.set_chat_administrator_custom_title(chat_id, user_id, custom_title)
    if is_success:
        await message.reply(f'Теперь {gender} {custom_title}')
    if user_id == users['acoola']:
        raise SkipHandler


async def unrestrict_and_promote_user(message: Message, user_id: int):
    chat_id = message.chat.id
    await message.chat.restrict(
        user_id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        )
    )
    if user_id == users['konako'] or user_id == users['evg'] or user_id == users['yura']:
        await promote(message, user_id, 1)
    else:
        await promote(message, user_id, 0)


async def silence(message: Message):
    args = message.get_args()
    if not args.isdigit():
        await message.reply('Укажи время в секундах')
        return
    if int(args) > 600:
        await message.reply('леее, не больше 10 минут')
        return

    try:
        user_id = message.reply_to_message.from_user.id
    except AttributeError:
        user_id = message.from_user.id
    title = await get_member_title(message, user_id)
    if not await restrict_user(message, user_id):
        return
    silence_info = await silence_info_check(user_id, title)
    if silence_info.is_silenced:
        await message.reply('Пользователь уже в муте')
        return
    async with Db() as db:
        await db.update_silences(user_id, True, title)
    await message.reply('Этот клоун теперь в муте')
    create_task(unsilence_delay(message, int(args)))


async def unsilence(message: Message):
    try:
        user_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.username
    except AttributeError:
        user_id = message.from_user.id
        username = message.from_user.username
    chat_id = message.chat.id
    async with Db() as db:
        silence_info = await silence_info_check(user_id)
        if not silence_info.is_silenced:
            if message.text == '/unmute':
                await message.reply('Пользователь еще не в муте')
                return
            else:
                return
        await db.update_silences(user_id, False, silence_info.title)

    await unrestrict_and_promote_user(message, user_id)
    while True:
        try:
            await message.bot.set_chat_administrator_custom_title(chat_id, user_id, silence_info.title)
        except:  # tg sucks ass and sometimes doesn't promote users correctly
            await restrict_user(message, user_id)
            await unrestrict_and_promote_user(message, user_id)
            await asyncio.sleep(5)
            logging.exception('Failed. Trying again.')
        else:
            break
    await message.answer(f'Пользователь @{username} больше не в муте')


async def devil_trigger(message: Message):
    async with Db() as db:
        all_devil_triggers = await db.get_all_devil_triggers()

    if not all_devil_triggers:
        await message_sender('Пополни базу далбаеб', test_group_id, message.bot)
        return
    audio_file_id = random.choice(all_devil_triggers)[0]
    await message.answer_audio(audio_file_id)


async def promote(message: Message, user_id: int = None, set_args: int = None):
    args = message.get_args()
    answer = 'no promotes for you'
    chat_id = message.chat.id
    if user_id is None:
        user_id = message.reply_to_message.from_user.id

    try:
        if set_args is None and message.reply_to_message is None:
            await message.reply('Перешли сообщение дуд')
            return
    except AttributeError:
        pass
    if (args == '' or set_args == 0) and set_args != 1:
        await message.bot.promote_chat_member(
            chat_id,
            user_id,
            can_invite_users=True,
            can_pin_messages=True,
            can_change_info=True,
            can_manage_chat=True,
            can_manage_voice_chats=True,
        )
        answer = 'promoted to admin'
    if args == 'giga' or set_args == 1:
        await message.bot.promote_chat_member(
            chat_id,
            user_id,
            can_invite_users=True,
            can_pin_messages=True,
            can_change_info=True,
            can_manage_chat=True,
            can_manage_voice_chats=True,
            can_promote_members=True,
            can_delete_messages=True,
            can_restrict_members=True
        )
        answer = 'promoted to giga admin'
        
    if set_args is None:
        try:
            await message.reply_to_message.reply(answer)
        except AttributeError:
            await message.reply(answer)
    if set_args is None:
        await message.delete()


async def niggers(message: Message):
    msg = 'пидорасы'
    if message.from_user.id == users['eger']:
        msg = 'сам ты пидор, а не негры'
    await message.reply(msg)


async def commands(message: Message):
    text = f'Список комманд:\n' \
           f'/кто - Команда которая преобразует введенное место и время в опрос. /format for more.\n' \
           f'/status - Статус майнкрафт сервера.\n' \
           f'/pasta - Рандомная паста.\n' \
           f'/say - Бесполезная матеша.\n' \
           f'/graveyard - Количество голубей на кладбище.\n' \
           f'/rollback - удаляет ласт фрейм из найс ав.\n' \
           f'/mute - запрещает пользователю писать в чат.\n' \
           f'/unmute - разрешает пользователю писать в чат.\n' \
           f'/set_title - ставит пользователю роль.\n' \
           f'Фичи:\n' \
           f'Словосочетания "голубь сдох" или "минус голубь" добавят одного голубя на кладбище.\n' \
           f'С некоторым шансом бот может кинуть медведя во время спама медведей.\n' \
           f'Кидает музяку на карточку Девил триггера.\n' \
           f'Меняет название конфы при заходе и ливе.\n'

    await message.answer(
        text=text,
    )


# TODO: add hpb to schedule
# async def happy_birthday(_):
# aps.add_job()


# TODO: random bad apple video


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
    dp.register_message_handler(delete_message, user_id=[users['konako'], users['gnome']], commands=['del'], chat_id=ls_group_id)
    # dp.register_message_handler(all, commands=['all'])
    # dp.register_message_handler(tmn, commands=['tmn'], chat_id=ls_group_id)
    # dp.register_message_handler(gamers, commands=['gamers'], chat_id=ls_group_id)
    # dp.register_message_handler(senat, commands=['senat'], chat_id=ls_group_id)
    dp.register_message_handler(timecode, regexp=re.compile(r'https://youtu\.be/', re.I), chat_id=ls_group_id)
    dp.register_message_handler(set_custom_title, commands=['set_title'], chat_id=ls_group_id)
    dp.register_message_handler(nice_pfp, nice_pfp_filter, chat_id=ls_group_id)
    dp.register_message_handler(nice_pfp, StickerFilter('AgAD0xAAAh3DcUk', is_nice=True), content_types=ContentTypes.STICKER, chat_id=ls_group_id)
    dp.register_message_handler(nice_pfp, StickerFilter('AgAD-BQAAs57cEk', is_nice=False), content_types=ContentTypes.STICKER, chat_id=ls_group_id)
    dp.register_message_handler(nice_pfp, StickerFilter('AgAD-hEAAuepaUk', is_nice=False), content_types=ContentTypes.STICKER, chat_id=ls_group_id)
    dp.register_message_handler(simp_moment, StickerFilter('AgADxhQAAvm9AUs'), content_types=ContentTypes.STICKER, chat_id=ls_group_id)
    dp.register_message_handler(devil_trigger, StickerFilter('AgAD_w4AAo5aWEk'), content_types=ContentTypes.STICKER, chat_id=ls_group_id)
    dp.register_message_handler(devil_trigger, StickerFilter('AgADpRQAAt8mkEs'), content_types=ContentTypes.STICKER, chat_id=ls_group_id)
    dp.register_message_handler(test, user_id=users['acoola'], chat_id=ls_group_id)
    dp.register_message_handler(commands, commands=['commands', 'c'], chat_id=ls_group_id)
    dp.register_message_handler(get_pic_from_num, commands=['pic'], chat_id=[test_group_id, ls_group_id])
    dp.register_message_handler(nice_pfp_rollback, commands=['rollback'], chat_id=ls_group_id, user_id=users['konako'])
    dp.register_message_handler(be_bra, regexp=re.compile(r'\bбе\b', re.I), chat_id=ls_group_id)
    dp.register_message_handler(niggers, regexp=re.compile(r'\bнегры\b', re.I), chat_id=ls_group_id)
    dp.register_message_handler(server_status, commands='status', chat_id=ls_group_id)
    # dp.register_message_handler(silence, commands=['mute'], chat_id=ls_group_id)
    # dp.register_message_handler(unsilence, commands=['unmute'], chat_id=ls_group_id)
    dp.register_message_handler(promote, commands=['promote'], chat_id=ls_group_id, user_id=users['konako'])
    dp.register_chat_member_handler(novichok, somebody_joined, chat_id=ls_group_id)
    dp.register_chat_member_handler(uzhe_smesharik, somebody_left, chat_id=ls_group_id)
