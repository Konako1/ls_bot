import re
from typing import Optional

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.handler import SkipHandler
from aiogram.types import Message, ChatMemberAdministrator, ForceReply, ChatMemberUpdated, ChatMemberOwner

from database.db import Db


class PingForm(StatesGroup):
    create_ping_command = State()
    delete_ping_command = State()
    add_user_to_ping_command = State()
    delete_user_from_ping_command = State()


async def add_user_in_command(message: Message, command: str) -> Optional[bool]:
    async with Db() as db:
        command_id = await db.get_ping_command_id(message.chat.id, command)
        if command_id == -1:
            await message.reply('Такой команды не существует.')
            return None
        await db.add_ping_user(message.from_user.id, message.from_user.username)
        result = await db.bind_command_user(message.from_user.id, command_id)
    if result is False:
        await message.reply('Пользователь уже был добавлен.')
        return False
    await message.reply('Пользователь был добавлен.')
    return True


async def is_ping_command_valid(command: str, message: Message) -> bool:
    result = re.findall(r'\W', command)
    if result:
        await message.reply('Был введен некорректный символ, напиши команду еще раз. '
                            'Допустимы только буквы, цифры и "_".\n/cancel для отмены.')
    return not result


async def create_ping_command_handler(message: Message, state: FSMContext):
    member = await message.chat.get_member(message.from_user.id)
    if not (isinstance(member, ChatMemberAdministrator) or isinstance(member, ChatMemberOwner)):
        await message.reply('Эта команда только для админов.')
        return
    command_list = await get_command_list(chat_id=message.chat.id)
    await message.reply(f'Напиши название команды, которая будет использоваться для пинга.\n{command_list}'
                        '/cancel для отмены.', reply_markup=ForceReply.create("Команда", selective=True))
    await state.set_state(PingForm.create_ping_command.state)


async def create_ping_command(message: Message, state: FSMContext):
    command = message.text.lower()
    if not await is_ping_command_valid(command, message):
        return
    await state.reset_state()
    async with Db() as db:
        await db.add_ping_command(message.chat.id, command)
    await message.reply(f'Команда /{command} была создана.')


async def delete_ping_command_handler(message: Message, state: FSMContext):
    member = await message.chat.get_member(message.from_user.id)
    if not (isinstance(member, ChatMemberAdministrator) or isinstance(member, ChatMemberOwner)):
        await message.reply('Эта команда только для админов.')
        return
    command_list = await get_command_list(message.chat.id)
    await message.reply(f'Напиши название команды, которую нужно удалить.\n{command_list}'
                        '/cancel для отмены.', reply_markup=ForceReply.create("Команда", selective=True))
    await state.set_state(PingForm.delete_ping_command.state)


async def delete_ping_command(message: Message, state: FSMContext):
    command = message.text.lower()
    if not await is_ping_command_valid(command, message):
        return
    await state.reset_state()
    async with Db() as db:
        command_id = await db.get_ping_command_id(message.chat.id, command)
        if command_id == -1:
            await message.reply('Такой команды не существует.')
            return
        await db.remove_command(command_id)
    await message.reply(f'Команда /{command} была удалена.')


async def add_user_to_command_handler(message: Message, state: FSMContext):
    args = message.get_args().lower()
    async with Db() as db:
        command_list = await db.get_all_ping_commands(message.chat.id)
    for command, _ in command_list:
        if args == command:
            result = await add_user_in_command(message, args)
            return
    command_list = await get_command_list(message.chat.id)
    if command_list is None:
        msg = f'В этом чате пока нет ни одной команды. /create_ping_command для создания новой.'
        markup = None
    else:
        msg = f'Напиши название команды, куда ты хочешь себя добавить.\n{command_list}/cancel для отмены.'
        markup = ForceReply.create("Команда", selective=True)
    await message.reply(msg, reply_markup=markup)
    await state.set_state(PingForm.add_user_to_ping_command.state)


async def add_user_to_command(message: Message, state: FSMContext):
    command = message.text.lower()
    if not await is_ping_command_valid(command, message):
        return
    result = await add_user_in_command(message, command)
    if result is None:
        return
    await state.reset_state()


async def delete_user_from_command_handler(message: Message, state: FSMContext):
    args = message.get_args().lower()
    command_list = await get_command_list(message.chat.id)
    if command_list is None:
        msg = f'В этом чате пока нет ни одной команды. /create_ping_command для создания новой.'
        markup = None
    else:
        msg = f'Напиши название команды, из который ты хочешь себя убрать.\n{command_list}/cancel для отмены.'
        markup = ForceReply.create("Команда", selective=True)
    await message.reply(msg, reply_markup=markup)
    await state.set_state(PingForm.delete_user_from_ping_command.state)


async def delete_user_from_command(message: Message, state: FSMContext):
    command = message.text.lower()
    if not await is_ping_command_valid(command, message):
        return
    async with Db() as db:
        command_id = await db.get_ping_command_id(message.chat.id, command)
        if command_id == -1:
            await message.reply('Такой команды не существует.')
            return
        is_deleted = await db.remove_user_from_command(command_id, message.from_user.id)
    await state.reset_state()
    if is_deleted:
        await message.reply('Успешно.')
        return
    await message.reply('Тебя в этой команде и не было.')


async def cancel_state(message: Message, state: FSMContext):
    await state.reset_state()
    await message.reply('Операция была отменена.')


async def ping_users(message: Message):
    command = message.text.lstrip('/').split(maxsplit=1)[0]
    async with Db() as db:
        command_id = await db.get_ping_command_id(message.chat.id, command)
        if command_id == -1:
            raise SkipHandler()
        usernames = await db.get_all_ping_usernames(command_id)
    if not usernames:
        await message.reply('В команде нет ни одного пользователя.')
        return
    msg = ''
    counter = 0
    for username in usernames:
        counter += 1
        msg += f'@{username[0]} '
        if counter == 5:
            await message.reply(msg)
            msg = ''
    await message.reply(msg)


async def get_command_list(chat_id: int) -> str:
    async with Db() as db:
        ping_commands = await db.get_all_ping_commands(chat_id)
    if not ping_commands:
        return ''
    msg = 'Список доступных команд для этого чата:\n'
    for command in ping_commands:
        msg += f'{command[0]}\n'
    return msg


async def get_user_command_list(chat_id: int, user_id: int) -> str:
    async with Db() as db:
        user_ping_commands = await db.get_all_ping_commands_for_user(chat_id, user_id)
    if not user_ping_commands:
        return ''
    msg = 'Список твоих команд:\n'
    for command in user_ping_commands:
        msg += f'{command}\n'
    return msg


async def get_available_commands(message: Message):
    msg = await get_command_list(message.chat.id)
    if msg == '':
        await message.reply('В этом чате нет ни одной команды.')
        return
    msg += 'Все команды прописываются через "/"'
    await message.reply(msg)


async def get_user_commands(message: Message):
    msg = await get_user_command_list(message.chat.id, message.from_user.id)
    if msg == '':
        await message.reply('Тебя нет ни в одной команде.')
        return
    msg += 'Все команды прописываются через "/"'
    await message.reply(msg)


async def delete_user_from_pings(event: ChatMemberUpdated):
    chat_id = event.chat.id
    username = event.from_user.username
    async with Db() as db:
        ping_commands = await db.get_all_ping_commands(chat_id)
    if ping_commands == '':
        return
    # todo


def setup(dp: Dispatcher):
    dp.register_message_handler(create_ping_command_handler, commands=['create_ping_command'])
    dp.register_message_handler(cancel_state, state=[
        PingForm.add_user_to_ping_command,
        PingForm.create_ping_command,
        PingForm.delete_ping_command,
        PingForm.delete_user_from_ping_command
    ], commands=['cancel'])
    dp.register_message_handler(create_ping_command, state=PingForm.create_ping_command, content_types=['text'])
    dp.register_message_handler(delete_ping_command_handler, commands=['delete_ping_command'])
    dp.register_message_handler(delete_ping_command, state=PingForm.delete_ping_command, content_types=['text'])
    dp.register_message_handler(add_user_to_command_handler, commands=['add_me'])
    dp.register_message_handler(add_user_to_command, state=PingForm.add_user_to_ping_command, content_types=['text'])
    dp.register_message_handler(delete_user_from_command_handler, commands=['delete_me'])
    dp.register_message_handler(delete_user_from_command, state=PingForm.delete_user_from_ping_command, content_types=['text'])
    dp.register_message_handler(get_available_commands, commands=['ping_commands'])
    dp.register_message_handler(get_user_commands, commands=['my_commands'])
    dp.register_message_handler(ping_users, Text(startswith='/'))
    # dp.register_chat_member_handler(delete_user_from_pings, utils.somebody_left)
