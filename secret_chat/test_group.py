from pprint import pprint

from aiogram import Dispatcher, Bot
from aiogram.types import Message, InputFile, MediaGroup, ContentTypes

from secret_chat.config import ls_group_id, test_group_id, frames_dir
from random import randint
from asyncio import create_task, sleep
from database import Db, StatType
from dataclasses import dataclass


@dataclass()
class FrameData:
    frame_count: int
    frames: list


async def say_to_ls(message: Message):
    args = message.text

    if args.startswith('/message'):
        await message.bot.send_message(ls_group_id, text=args.removeprefix('/message '))


async def add_paste(message: Message):
    args = message.text
    async with Db() as db:
        if args.startswith('/add'):
            await db.add_paste(text=args.removeprefix('/add '))
            await message.reply('ok')


def sort_top_frames(frames: list[(int, int)]) -> FrameData:
    max_count = 0
    frame_list = list()
    for frame in frames:
        if frame[1] > max_count:
            max_count = frame[1]
            frame_list.clear()
        if max_count == frame[1]:
            frame_list.append(frame[0])
    return FrameData(
        frame_count=max_count,
        frames=frame_list,
    )


async def nice_pfp_counter(message: Message):
    mg = MediaGroup()
    async with Db() as db:
        frames_count_all = await db.get_statistics(StatType().nice_pfp)
        frames_data = await db.get_frames_data()

    f_sorted = sort_top_frames(frames_data)
    frames_count = len(f_sorted.frames)
    print(frames_count)
    if frames_count > 10:
        r = randint(0, frames_count - 10)
        s = slice(r, r + 10)
    else:
        s = slice(0, frames_count)
    for frame in f_sorted.frames[s]:
        mg.attach_photo(InputFile(frames_dir + f'pic{str(frame)}.jpg'), caption=frame)
    await message.bot.send_media_group(test_group_id, mg)

    answer = 'Стата по авам:'
    for i in f_sorted.frames:
        answer += f'\n{i} сохранено: {f_sorted.frame_count} штук'
    answer += f'\nВсего найс ав: {frames_count_all}.'
    await message.answer(answer)


async def get_similar_nice_pfp(message: Message):
    async with Db() as db:
        frames = await db.get_frames_data()  # type: list[(int, int)]
    frames.sort()
    similar_frames = list()
    for i, frame in enumerate(frames):
        if i + 1 == len(frames):
            break
        if frames[i + 1][0] - frames[i][0] < 3:
            similar_frames.append((frames[i][0], frames[i + 1][0]))
    create_task(answer_similar_pfp(message, similar_frames))


async def answer_similar_pfp(message: Message, similar_frames: list):
    for f_tuple in similar_frames:
        await message.bot.send_chat_action(message.chat.id, 'upload_photo')
        mg = MediaGroup()
        mg.attach_photo(InputFile(frames_dir + f'pic{str(f_tuple[0])}.jpg'), caption=f'{str(f_tuple[0])} | {str(f_tuple[1])}')
        mg.attach_photo(InputFile(frames_dir + f'pic{str(f_tuple[1])}.jpg'))
        await message.answer_media_group(mg)
        await sleep(5)
    await message.answer(f'Всего {str(len(similar_frames) * 2)} похожих кадров.')


async def get_say_numbers() -> tuple[str, str, int]:
    async with Db() as db:
        highest_num = await db.get_num('positive')
        lowest_num = await db.get_num('negative')
        say_count = await db.get_statistics(StatType.say)

    highest_num_str = get_num_as_pow(highest_num)
    lowest_num_str = get_num_as_pow(lowest_num)
    return highest_num_str, lowest_num_str, say_count


def get_num_as_pow(num: float) -> str:
    whole_fraction = 4 if num < 0 else 3
    return f'{str(num)[:whole_fraction]} * 10^{len(str(num)) - whole_fraction}'


async def get_say_statistics(message: Message):
    highest, lowest, say_count = await get_say_numbers()
    await message.bot.send_message(
        text=f'Say stats:\ncount — {say_count}\nlowest — {lowest}\nhighest — {highest}',
        chat_id=test_group_id,
    )


async def add_devil_trigger_to_db(message: Message):
    async with Db() as db:
        if message.reply_to_message is None or message.reply_to_message.audio is None:
            await message.reply('Реплайни аудио девил триггера')
            return
        answer = await db.add_devil_trigger(message.reply_to_message.audio.file_id)

    if answer:
        await message.reply('Музяка добавлена')
    else:
        await message.reply('Чето пошло по пизде')


async def help(message: Message):
    await message.bot.send_message(
        text=f"/message - send message to test_group\n"
             f"/add - add paste to db\n"
             f"/nice_pfp - get nice_pfp count\n"
             f"/say - get say statistics\n"
             f"/pic - get pic from number\n"
             f"/get_similar_pfp - returns similar pfp",
        chat_id=test_group_id,
    )


def setup(dp: Dispatcher):
    dp.register_message_handler(say_to_ls, commands=['message', 'm'], chat_id=test_group_id)
    dp.register_message_handler(add_paste, commands=['add'], chat_id=test_group_id)
    dp.register_message_handler(nice_pfp_counter, commands=['nice_pfp', 'nice_ava'], chat_id=test_group_id)
    dp.register_message_handler(get_similar_nice_pfp, commands=['get_similar_pfp'], chat_id=test_group_id)
    dp.register_message_handler(add_devil_trigger_to_db, commands=['dt'], chat_id=test_group_id)
    dp.register_message_handler(help, commands=['help', 'commands', 'c'], chat_id=test_group_id)
