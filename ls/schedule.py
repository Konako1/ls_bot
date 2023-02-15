import datetime

from aiogram import Dispatcher
from aiogram.types import Message

from database import Db
from modeus.id_finder_modeus import get_json_id
from modeus.modeus_parser import get_schedule


async def save_modeus_fio(message: Message):
    if message.get_args() == '':
        return await message.reply('Впиши ФИО вместе с командой')

    modeus_id = await get_json_id(message.get_args(), datetime.datetime.now().strftime('%Y-%m-%d'))

    if modeus_id is None:
        return await message.reply('Введи корректное ФИО')

    async with Db() as db:
        await db.add_modeus_user(message.from_user.id, modeus_id)

    await message.reply('ФИО сохранено')


async def next_para(message: Message):
    fio = None if message.get_args() == '' else message.get_args()
    user_id = message.from_user.id
    modeus_id = None
    if fio is None:
        async with Db() as db:
            modeus_id = await db.get_modeus_id(user_id)
            if modeus_id is None:
                return await message.reply('Либо впиши ФИО, либо /save_my_modeus_fio + ФИО')

    now = datetime.datetime.now()
    paras = await get_schedule(fio, modeus_id, now.strftime('%Y-%m-%d'))
    if paras is None:
        return await message.reply('Введи корректное ФИО')
    p_next = None
    for para in paras:
        if now < para['end_time']:
            p_next = para
            break

    days = (p_next['start_time'].date() - now.date()).days
    text = f'{p_next["short_name"]}\n' \
           f'<b>{p_next["start_time"].strftime("%H:%M")}-{p_next["end_time"].strftime("%H:%M")}</b>{" | " + str(p_next["start_time"].date()) if days != 0 else ""}\n' \
           f'Кабинет {p_next["room"]}'

    await message.reply(text)


def setup(dp: Dispatcher):
    dp.register_message_handler(next_para, commands=['next'])
    dp.register_message_handler(save_modeus_fio, commands=['save_modeus_fio'])
