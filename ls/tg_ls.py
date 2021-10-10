from datetime import datetime
import random

import vk_api
from database import Db
from utils import delayed_delete
from secret_chat.simple_math import math
from secret_chat.test_group import get_say_statistics, get_num_as_pow
from aiogram import Dispatcher
from aiogram.types import Message, ContentTypes, InputFile
from aiogram.dispatcher.filters import Text
from secret_chat.config import test_group_id, spring_05_preview_direction
from asyncio import create_task
from utils import StickerFilter
from database import StatType, StickerInfo

vk = vk_api.Vk()


async def colon_check(message: Message, time: str):
    time_h, time_m = time.split(':')
    if int(time_h) >= 24:
        await message.reply('Научись писать время, ебанат')
        raise ValueError
    if int(time_m) >= 60:
        await message.reply('Научись писать время, ебанат')
        raise ValueError


def time_calculator():
    time = ''
    if datetime.now().minute < 15:
        time = f'{datetime.now().hour}:30'
    elif datetime.now().minute in range(15, 31):
        time = f'{datetime.now().hour}:45'
    elif datetime.now().minute in range(31, 46):
        time = f'{datetime.now().hour + 1}:00'
    elif datetime.now().minute > 45:
        time = f'{datetime.now().hour + 1}:15'
    return time


async def empty_args():
    time = time_calculator()
    place = 'Борщ'
    return time, place


async def one_arg(args: str, now: list[str], message: Message, multiple_args: bool):
    if multiple_args:
        time = ''
        place = args
        return time, place
    if args.split(' ')[0].isalpha() and args.split(' ')[0] not in now:
        time = time_calculator()
        place = args.split(' ')[0]
        return time, place
    else:
        time = args.split(' ')[0]
        place = 'Борщ'
        time = await right_time_check(time, message)
        return time, place


def split_checker(position: int, args: str, now: list[str]):
    is_in_now = False
    colon = False
    is_arg_num = False

    if position == 0:
        if args.split(' ', maxsplit=1)[position].lower() in now:
            is_in_now = True

        if args.split(' ', maxsplit=1)[position].count(':') > 0:
            colon = True

        if int(args.split(' ', maxsplit=1)[position].isnumeric()):
            is_arg_num = True

        return is_in_now, colon, is_arg_num

    if args.rsplit(' ', maxsplit=1)[position].lower() in now:
        is_in_now = True

    if args.rsplit(' ', maxsplit=1)[position].count(':') > 0:
        colon = True

    if int(args.rsplit(' ', maxsplit=1)[position].isnumeric()):
        is_arg_num = True

    return is_in_now, colon, is_arg_num


async def two_args(now: list[str], args: str, message: Message):
    is_in_now, colon, is_arg_num = split_checker(0, args, now)

    if is_in_now or colon or is_arg_num:
        time, place = args.rsplit(' ', maxsplit=1)
        if not is_in_now:
            time = await right_time_check(time, message)
        return time, place

    is_in_now, colon, is_arg_num = split_checker(1, args, now)

    if is_in_now or colon or is_arg_num:
        place, time = args.rsplit(' ', maxsplit=1)
        if not is_in_now:
            time = await right_time_check(time, message)
        return time, place

    multiple_args = True
    time, place = await one_arg(args, now, message, multiple_args)
    return time, place


async def get_time(message: Message, args: str) -> tuple[str, str]:
    now = ['щас', "сейчас", "now", "епта", "ёпта", "завтра", "вечером", "утром", "ночью", "днем", "днём", "скоро",
           "никогда"]

    if args != '':
        args = args.removeprefix(' ')

    if args == '':
        time, place = await empty_args()
        return time, place

    if len(args.split(' ')) == 1:
        time, place = await one_arg(args, now, message, False)
        return time, place

    time, place = await two_args(now, args, message)
    return time, place


async def right_time_check(time: str, message: Message):
    if time.count('-') == 1:
        time_split = time.split('-')
        for count in range(len(time_split)):
            if time_split[count].count(':') > 0:
                await colon_check(message, time_split[count])
                return time

    if time.count(':') == 1:
        await colon_check(message, time)
        return time

    if int(time) > 23:
        await message.reply('Научись писать время, ебанат')
        raise ValueError

    if time in ('1', '21'):
        if time == '1':
            time = 'Час'
        else:
            time = f'{time} час'
        return time

    if int(time) in range(2, 5) or int(time) in range(22, 24):
        time = f'{time} часа'
        return time

    time = f'{time} часов'
    return time


async def say(message: Message):
    if message.chat.id == test_group_id:
        await get_say_statistics(message)
        return

    message_text, num, is_funny_number = math(
        message.from_user.first_name,
        message.chat.id
    )

    db = Db()

    if num > 0:
        saved_num = await db.get_num('positive')
        if num > saved_num:
            print(f'New highest num: {get_num_as_pow(num)}')
            await db.update_num(num)
    elif num < 0:
        saved_num = await db.get_num('negtive')
        if num < saved_num:
            print(f'New lowest num: {get_num_as_pow(num)}')
            await db.update_num(num)

    msg = await message.answer(text=message_text)
    await message.delete()
    if not is_funny_number:
        create_task(delayed_delete(msg, 15))

    await db.update_stat(StatType.say)


async def pasta(message: Message):
    db = Db()
    count = await db.get_paste_count()
    offset = random.randint(0, count)
    paste = await db.get_paste(offset)
    msg = await message.reply(text=paste)
    create_task(delayed_delete(msg, 300))
    create_task(delayed_delete(message, 300))


# TODO: кикать чела если он юзанул команду kekw
# async def all(message: Message):
    # users = message.chat.unban()


async def smart_poll(message: Message):
    args = message.get_args()

    time, place = await get_time(args=args, message=message)
    options = ['Я', 'Мб я', 'Не я']
    dot = '.'

    if time == '':
        dot = ''
        if place.lower() == 'я.':
            options = ['Пидорас', 'Педофил']

    await message.answer_poll(
        question=f'{time.capitalize()}{dot} {place.capitalize()}. Кто.',
        options=options,
        is_anonymous=False
    )
    await message.delete()


async def bear(message: Message):
    db = Db()
    unique_id = message.sticker.file_unique_id
    sticker_info = await db.get_sticker_info(unique_id)
    msg_date = message.date.timestamp()
    time_calc = msg_date - sticker_info.date.timestamp()
    if time_calc < 240:
        rnd = random.choice(range(sticker_info.probability))
        if rnd == 0:
            await message.answer_sticker(
                sticker='CAACAgIAAxkBAAECH0VgYjnrZnEhC9I3mjXeIlJZVf4osQACXAADDnr7CuShPCAcZWbPHgQ'
            )
            print(f"it's bear time in group {message.chat.title}\nprob was: {round(1 / sticker_info.probability, 2)}\n")
            await db.update_sticker(StickerInfo(
                name=unique_id,
                date=message.date,
                probability=10,
                count=sticker_info.count + 1
            ))
            return
    await db.update_sticker(StickerInfo(
        name=unique_id,
        date=message.date,
        probability=sticker_info.probability - 1,
        count=sticker_info.count
    ))


async def minus_chel(message: Message):
    text = message.text.lower()
    if 'сдох' in text or 'минус' in text:
        await message.reply('Помянем.')
        db = Db()
        await db.update_stat(StatType.pigeon)


async def get_graves_count(message: Message):
    db = Db()
    count = await db.get_statistics(StatType.pigeon)
    await message.reply(text=f'Голубей подохло: {count}')


# TODO: замутить вызов операции подсчета кол-ва постов на стене только 1 раз
# TODO: приделать картинки к меседжу, если он есть
async def get_anek(message: Message):
    post_count = await vk.get_akb_post_count()
    offset = random.randint(0, post_count)

    funny = await vk.get_funny(vk_api.akb_group, 1, offset)
    if not funny:
        await get_anek(message)
        return

    anek = random.choice(funny)
    msg = await message.reply(anek)

    create_task(delayed_delete(msg, 300))
    create_task(delayed_delete(message, 300))
    db = Db()
    await db.update_stat(StatType.anek)

    print(f'анек номер {offset}')


async def kto_format(message: Message):
    text = f'/кто - [округленное_время]. Борщ. Кто.\n' \
           f'/кто [время] - [время]. Борщ. Кто.\n' \
           f'/кто [место] - [округленное_время]. [место]. Кто.\n' \
           f'/кто [место] [время] (порядок не важен) - [время]. [место]. Кто.\n' \
           f'/кто [рандомное предложение] - [рандомное предложение]. Кто.\n' \
           f'Формат времени:\n' \
           f'11; 11:11; 11-11:11 слова, такие как "вечером", "сейчас", "now", "епта" и тд.\n' \
           f'Если вы тупой и не знаете как правильно писать часы и минуты, то бот вам об этом сообщит.'

    await message.reply(
        text=text,
    )


async def features(message: Message):
    await message.reply(
        text=f'Фичи:\n'
             f'Словосочетания "голубь сдох" или "минус голубь" добавят одного голубя на кладбище.\n'
             f'С некоторым шансом бот может кинуть медведя во время спама медведей.'
    )


def setup(dp: Dispatcher):
    dp.register_message_handler(smart_poll, commands=['kto', 'кто'])
    dp.register_message_handler(pasta, commands=['pasta'])
    dp.register_message_handler(say, commands=['say'])
    dp.register_message_handler(kto_format, commands=['format'])
    dp.register_message_handler(bear, StickerFilter('AgADXAADDnr7Cg'), content_types=ContentTypes.STICKER)
    dp.register_message_handler(minus_chel, Text(contains='голубь', ignore_case=True))
    dp.register_message_handler(get_graves_count, commands=['graveyard'])
    dp.register_message_handler(get_anek, commands=['anek'])
    dp.register_message_handler(features, commands=['features'])
