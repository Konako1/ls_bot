from datetime import datetime
import random
import time

import vk_api
from methods.methods import delayed_delete
from secret_chat.paste_updater import PasteUpdater
from secret_chat.stickers import Stickers
from secret_chat.simple_math import Calls, math
from secret_chat.test_group import get_say_statistics, get_num_as_pow
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ContentTypes, InputFile, MediaGroup
from aiogram.dispatcher.filters import Text
from secret_chat.config import ls_group_id, test_group_id, spring_05_preview_direction
from asyncio import create_task
from pprint import pprint

calls = Calls()
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

    num_len = len(str(num))
    if num > 0:
        saved_num = calls.get_highest_num()
        if num_len >= saved_num.digit:
            if num > saved_num.number:
                print(f'New highest num: {get_num_as_pow(num)}')
                calls.update_highest_num(num, num_len)
    elif num < 0:
        saved_num = calls.get_lowest_num()
        if num_len >= saved_num.digit:
            if num < saved_num.number:
                print(f'New lowest num: {get_num_as_pow(num)}')
                calls.update_lowest_num(num, num_len)

    msg = await message.answer(text=message_text)
    await message.delete()
    if not is_funny_number:
        create_task(delayed_delete(msg, 15))

    calls.say_was_sayed()


async def pasta(message: Message):
    pastes = PasteUpdater()
    msg = await message.reply(text=pastes.get_random_paste())
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
    args = message.sticker.file_unique_id

    if args == 'AgADXAADDnr7Cg':
        stickers = Stickers()
        sticker_date, sticker_prob = stickers.get_bear_values()
        msg_date = message.date
        time_calc = msg_date - sticker_date
        if time_calc.seconds < 240:
            rnd = random.choice(range(sticker_prob))
            if rnd == 0:
                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAECH0VgYjnrZnEhC9I3mjXeIlJZVf4osQACXAADDnr7CuShPCAcZWbPHgQ'
                )
                print(f"it's bear time in group {message.chat.title}\nprob was: {round(1 / sticker_prob, 2)}\n")
                stickers.update_bear_values(msg_date, 10)
                return
        stickers.update_bear_values(msg_date, sticker_prob - 1)


async def minus_chel(message: Message):
    text = message.text.lower()
    if 'сдох' in text or 'минус' in text:
        await message.reply('Помянем.')
        calls.golub_was_found()


async def get_graves_count(message: Message):
    await message.reply(text=f'Голубей подохло: {calls.get_deaths_count()}')


async def set_number_one_on_spring_05(message: Message):
    args = message.get_args().split(' ')
    if len(args) != 2:
        await message.reply('Пошел нахуй идиот')
        return

    try:
        time = round(float(args[1]), 3)
        name = args[0]
    except ValueError:
        await message.reply('Пошел нахуй идиот')
        return

    previous_record = calls.get_number_one_time()
    if previous_record < time:
        await message.reply('Чет слабовато, иди ка ты нахуй')
        return
    elif time < 27:
        await message.reply('Нихуя ты быстрый, читераст наверное, иди ка ты нахуй')
        return

    calls.update_number_one_name(name)
    calls.update_number_one_time(time)

    await message.reply('Нихуя, жесть ты крут')
    await message.answer_sticker(
        sticker='CAACAgIAAxkBAAECda5g0n3sq6IZp8b2AAGlYr8b8EM6jEEAArMABJrPDSU5w8aXOEktHwQ',
    )


async def get_number_one_on_spring_05(message: Message):
    time = calls.get_number_one_time()
    name = calls.get_number_one_name()
    text = f'Топ1 Курганской Области на Spring 05:\n{name} - {time}'

    await message.reply_photo(
        photo=InputFile(spring_05_preview_direction),
        caption=text,
    )


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
    dp.register_message_handler(bear, content_types=ContentTypes.STICKER)
    dp.register_message_handler(minus_chel, Text(contains='голубь', ignore_case=True))
    dp.register_message_handler(get_graves_count, commands=['graveyard'])
    dp.register_message_handler(get_number_one_on_spring_05, commands=['get_top1'])
    dp.register_message_handler(set_number_one_on_spring_05, commands=['update_top1'])
    dp.register_message_handler(get_anek, commands=['anek'])
    dp.register_message_handler(features, commands=['features'])
