import aiogram
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

from secret_chat.config import users, ls_group_id, test_group_id, frames_dir
from datetime import datetime
from utils import StickerFilter, nice_pfp_filter, message_sender
from asyncio import create_task, sleep
# from database import Db, StatType, SilenceInfo

import re



async def is_ping_command_valid(command: str, message: Message) -> bool:
    result = re.findall(r'\W', command)
    if result:
        await message.reply('Был введен некорректный символ, напиши команду еще раз. '
                            'Допустимы только буквы, цифры и "_".\n/cancel для отмены.')
    return not result


async def create_ping_command_handler(message: Message, state: FSMContext):
    member = await message.chat.get_member(message.from_user.id)
    if not isinstance(member, ChatMemberAdministrator):
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
    if not isinstance(member, ChatMemberAdministrator):
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
    async with Db() as db:
        command_id = await db.get_ping_command_id(message.chat.id, command)
        if command_id == -1:
            await message.reply('Такой команды не существует.')
            return
        await db.add_ping_user(message.from_user.id, message.from_user.username)
        result = await db.bind_command_user(message.from_user.id, command_id)
    await state.reset_state()
    if result is False:
        await message.reply('Пользователь уже был добавлен.')
        return
    await message.reply('Пользователь был добавлен.')


async def delete_user_from_command_handler(message: Message, state: FSMContext):
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
    command = message.text.lstrip('/')
    async with Db() as db:
        command_id = await db.get_ping_command_id(message.chat.id, command)
        if command_id == -1:
            return
        usernames = await db.get_all_ping_usernames(command_id)
    if not usernames:
        await message.reply('В команде нет ни одного пользователя.')
        return
    msg = ''
    for username in usernames:
        msg += f'@{username[0]} '
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

