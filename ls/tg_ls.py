from datetime import datetime
import random
from typing import Dict
import vk_api
from database import Db
from utils import delayed_delete
from secret_chat.simple_math import math
from secret_chat.test_group import get_say_statistics, get_num_as_pow
from aiogram import Dispatcher
from aiogram.types import Message, ContentTypes, InputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageTextIsEmpty
from aiogram.utils.callback_data import CallbackData
from secret_chat.config import test_group_id, spring_05_preview_direction
from asyncio import create_task
from utils import StickerFilter
from database import StatType, StickerInfo

vk = vk_api.Vk()

callback_data = CallbackData('anek', 'anek_id', 'action')


async def say(message: Message):
    if message.chat.id == test_group_id:
        await get_say_statistics(message)
        return

    message_text, num, is_funny_number = math(
        message.from_user.first_name,
        message.chat.id
    )

    async with Db() as db:
        if num > 0:
            saved_num = await db.get_num('positive')
            if num > saved_num:
                print(f'New highest num: {get_num_as_pow(num)}')
                await db.update_num(num)
        elif num < 0:
            saved_num = await db.get_num('negative')
            if num < saved_num:
                print(f'New lowest num: {get_num_as_pow(num)}')
                await db.update_num(num)

        msg_answer = await message.answer(text=message_text)

        if not is_funny_number:
            create_task(delayed_delete(message, 15))
            create_task(delayed_delete(msg_answer, 15))

        await db.update_stat(StatType.say)


async def pasta(message: Message):
    async with Db() as db:
        count = await db.get_paste_count()
        offset = random.randint(0, count)
        paste = await db.get_paste(offset)
    try:
        msg = await message.reply(text=paste)
    except MessageTextIsEmpty as e:
        msg = await message.reply(text=f'Чет я нихуя не нашел, ну а хули, {e} же')
    create_task(delayed_delete(msg, 300))
    create_task(delayed_delete(message, 300))


# TODO: кикать чела если он юзанул команду kekw
# async def all(message: Message):
    # users = message.chat.unban()


async def bear(message: Message):
    async with Db() as db:
        unique_id = message.sticker.file_unique_id
        sticker_info = await db.get_sticker_info(unique_id)
        if sticker_info is None:
            await db.update_sticker(StickerInfo(
                name=unique_id,
                date=message.date,
                probability=10,
                count=1
            ))
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
        async with Db() as db:
            await db.update_stat(StatType.pigeon)


async def get_graves_count(message: Message):
    async with Db() as db:
        count = await db.get_statistics(StatType.pigeon)
    await message.reply(text=f'Голубей подохло: {count}')


# TODO: замутить вызов операции подсчета кол-ва постов на стене только 1 раз
# TODO: приделать картинки к меседжу, если он есть
async def get_anek(message: Message):
    if message.get_args() == '':
        await get_random_anek(message)
        return
    await get_anek_from_number(message)


async def get_random_anek(message: Message):
    post_count = await vk.get_akb_post_count()
    anek_id = random.randint(0, post_count)

    funny = await vk.get_funny(vk_api.akb_group, 1, anek_id)
    if not funny:
        await get_random_anek(message)
        return

    anek = random.choice(funny)
    inline = await create_inline_keyboard(anek_id)
    msg = await message.reply(anek, reply_markup=inline)

    create_task(delayed_delete(msg, 300))
    create_task(delayed_delete(message, 300))
    async with Db() as db:
        await db.update_stat(StatType.anek)

    print(f'анек номер {anek_id}')


async def get_anek_from_number(message: Message):
    post_count = await vk.get_akb_post_count()
    try:
        anek_id = int(message.get_args())
        if anek_id > post_count:
            await message.reply(f'Номер анека должен быть меньше чем {post_count}')
            return
    except ValueError or TypeError:
        await message.reply(f'Сука число впиши')
        return
    funny = await vk.get_funny(vk_api.akb_group, 1, anek_id)
    if not funny:
        await message.reply('Анека не существует')
        return
    inline = await create_inline_keyboard(anek_id)
    anek = funny[0]
    await message.reply(anek, reply_markup=inline)
    async with Db() as db:
        await db.update_stat(StatType.anek)


async def create_inline_keyboard(anek_id: int) -> InlineKeyboardMarkup:
    haha_count, not_haha_count = await get_anek_data(anek_id)
    kb = InlineKeyboardMarkup(row_width=3, ).row(
        InlineKeyboardButton(f'{haha_count}x Haha', callback_data=callback_data.new(anek_id=anek_id, action='haha')),
        InlineKeyboardButton(f"{not_haha_count}x Hahan't", callback_data=callback_data.new(anek_id=anek_id, action='not_haha')),
        InlineKeyboardButton('Оставить', callback_data=callback_data.new(anek_id=anek_id, action='save')),
    )
    return kb


async def get_anek_data(anek_id: int) -> tuple[int, int]:
    haha = 0
    not_haha = 0

    async with Db() as db:
        data = await db.get_anek_data(anek_id)  # type: list[tuple]
        if data is None:
            return 0, 0

        for reaction in data:
            if int(reaction[0]) == 1:
                haha += 1
            else:
                not_haha += 1
    return haha, not_haha


async def haha_handler(query: CallbackQuery, callback: Dict[str, str]):
    await query.answer('Hihi')
    async with Db() as db:
        anek_id = int(callback['anek_id'])
        await db.update_anek_data(anek_id, query.from_user.id, True)

    new_kb = await create_inline_keyboard(anek_id)
    await query.message.edit_reply_markup(new_kb)


async def not_haha_handler(query: CallbackQuery, callback: Dict[str, str]):
    await query.answer('No hihi :(')
    async with Db() as db:
        anek_id = int(callback['anek_id'])
        await db.update_anek_data(anek_id, query.from_user.id, False)

    new_kb = await create_inline_keyboard(anek_id)
    await query.message.edit_reply_markup(new_kb)


async def save_anek(query: CallbackQuery, callback: Dict[str, str]):
    await query.answer('WIP')


async def get_last_anek(message: Message):
    pass  # TODO


async def features(message: Message):
    await message.reply(
        text=f'Фичи:\n'
             f'Словосочетания "голубь сдох" или "минус голубь" добавят одного голубя на кладбище.\n'
             f'С некоторым шансом бот может кинуть медведя во время спама медведей.'
    )


def setup(dp: Dispatcher):
    dp.register_message_handler(pasta, commands=['pasta'])
    dp.register_message_handler(say, commands=['say'])
    dp.register_message_handler(bear, StickerFilter('AgADXAADDnr7Cg'), content_types=ContentTypes.STICKER)
    dp.register_message_handler(minus_chel, Text(contains='голубь', ignore_case=True))
    dp.register_message_handler(get_graves_count, commands=['graveyard'])
    dp.register_message_handler(get_anek, commands=['anek'])
    dp.register_message_handler(features, commands=['features'])
    dp.callback_query_handler(haha_handler, callback_data.filter(action='haha'))
    dp.callback_query_handler(not_haha_handler, callback_data.filter(action='not_haha'))
