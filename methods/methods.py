from aiogram.types import Message
from aiogram.utils.exceptions import MessageToDeleteNotFound
from asyncio import sleep


async def delayed_delete(message: Message, sec: int):
    await sleep(sec)
    try:
        await message.delete()
    except MessageToDeleteNotFound as e:
        print(f'Какой то ебалай удалил сообщение, потому лови {e} себе в ебальник')