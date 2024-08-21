import datetime

from aiogram import Dispatcher
from aiogram.types import Message

from database.db import Db
from modeus.modeus_api import ModeusApi
from modeus.utils import user_filter, prepare_request, fc_filter, \
    format_event_final_text, day_fio_split


async def save_modeus_fio(message: Message, modeus_api: ModeusApi):
    if not modeus_api.access_token:
        await message.reply('Сервер сдох')
        return
    if message.get_args() == '':
        return await message.reply('Впиши ФИО вместе с командой')

    modeus_users = await modeus_api.search_user(message.get_args())
    user_text = user_filter(modeus_users)
    if user_text is not None:
        return await message.reply(user_text)
    modeus_user = modeus_users[0]
    async with Db() as db:
        await db.add_modeus_user(message.from_user.id, modeus_user['id'])

    await message.reply('ФИО сохранено')


async def fc_toggle(message: Message):
    async with Db() as db:
        modeus_id = await db.get_modeus_id(message.from_user.id)
        if modeus_id is None:
            return await message.reply('Тебя нет в базе, либо впиши ФИО, либо /save_modeus_fio + ФИО')
        is_fc = bool(await db.get_modeus_fc_toggle(message.from_user.id))
        new_is_fc = False if is_fc else True
        await db.update_modeus_fc_toggle(message.from_user.id, modeus_id, int(new_is_fc))
    text = 'Физра включена в выдачу' if new_is_fc else 'Физра отключена из выдачи'
    await message.reply(text)


async def paras_today(message: Message, modeus_api: ModeusApi):
    if not modeus_api.access_token:
        await message.reply('Сервер сдох')
        return
    # allows to do "FIO +1" where +1 is one day
    fio, append_days = day_fio_split(message.get_args())
    if not (0 <= append_days <= 7):
        return await message.reply('Можно смотреть пары максимум на неделю вперед')

    result = await prepare_request(message, modeus_api, fio)
    if not result[0]:
        return await message.reply(result[1])
    modeus_id = result[1]

    unsorted_events = await modeus_api.get_schedule(modeus_id)
    if unsorted_events is None:
        return await message.reply('Введи корректное ФИО')

    events = await fc_filter(message.from_user.id, unsorted_events)
    now = datetime.datetime.now(events[0]['end'].tzinfo).date() + datetime.timedelta(days=append_days)

    # main filter
    is_events = False
    text = 'Пары на день:\n\n'
    for event in events:
        if now == event['end'].date():
            text += format_event_final_text(event) + '\n\n✨✨✨✨✨✨✨✨\n\n'
            is_events = True
    text = text if is_events else 'Пар нет 🎉'
    await message.reply(text.rstrip('\n\n✨✨✨✨✨✨✨✨\n\n'))


async def next_para(message: Message, modeus_api: ModeusApi):
    if not modeus_api.access_token:
        await message.reply('Сервер сдох')
        return
    result = await prepare_request(message, modeus_api, message.get_args())
    if not result[0]:
        return await message.reply(result[1])
    modeus_id = result[1]

    unsorted_events = await modeus_api.get_schedule(modeus_id)
    if unsorted_events is None:
        return await message.reply('Введи корректное ФИО')

    events = await fc_filter(message.from_user.id, unsorted_events)
    now = datetime.datetime.now(events[0]['end'].tzinfo)

    # main filter
    next_event = None
    for event in events:
        if now < event['end'] - datetime.timedelta(minutes=45):
            next_event = event
            break

    text = format_event_final_text(next_event) if next_event is not None else 'Пар нет 🎉'
    await message.reply(text)


def setup(dp: Dispatcher):
    dp.register_message_handler(next_para, commands=['next', 'n'])
    dp.register_message_handler(paras_today, commands=['day', 'd'])
    dp.register_message_handler(fc_toggle, commands=['fc_toggle'])
    dp.register_message_handler(save_modeus_fio, commands=['save_modeus_fio'])
