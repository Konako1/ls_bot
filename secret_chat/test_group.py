from aiogram import Dispatcher, Bot
from aiogram.types import Message, InputFile, MediaGroup

from secret_chat.config import ls_group_id, test_group_id, frames_dir
from secret_chat.simple_math import Calls
from secret_chat.frames import Frames
from secret_chat.paste_updater import PasteUpdater
from random import randint
from asyncio import create_task, sleep

async def say_to_ls(message: Message):
    args = message.text

    if args.startswith('/message'):
        await message.bot.send_message(ls_group_id, text=args.removeprefix('/message '))


async def add_paste(message: Message):
    args = message.text
    pastes = PasteUpdater()
    if args.startswith('/add'):
        pastes.add_paste(text=args.removeprefix('/add '))
        pastes.save()
        await message.reply('ok')


async def nice_pfp_counter(message: Message):
    calls = Calls()
    frames = Frames()
    mg = MediaGroup()

    frames_count = calls.get_nice_pfp_calls()
    frames, this_frame_count = frames.get_nicest_frame()
    count = len(frames)
    if count > 10:
        r = randint(0, count - 10)
        s = slice(r, r + 10)
    else:
        s = slice(0, count)
    for i, frame in enumerate(frames[s]):
        mg.attach_photo(InputFile(frames_dir + f'pic{str(frame)}.jpg'), caption=frame)

    await message.bot.send_media_group(test_group_id, mg)
    await message.answer(f'Таких ав сохранено: {this_frame_count}\nВсего найс ав: {frames_count}.')


async def get_similar_nice_pfp(message: Message):
    _frames = Frames()

    frames = _frames.get_all_frames()  # type: list[int]
    frames.sort()
    similar_frames = list()
    for i, frame in enumerate(frames):
        if i + 1 == len(frames):
            break
        if frames[i + 1] - frames[i] < 3:
            similar_frames.append((frames[i], frames[i + 1]))
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


def get_say_numbers() -> tuple[str, str, int]:
    calls = Calls()
    highest_num = calls.get_highest_num().number
    lowest_num = calls.get_lowest_num().number
    say_count = calls.get_say_count()

    highest_num_str = get_num_as_pow(highest_num)
    lowest_num_str = get_num_as_pow(lowest_num)
    return highest_num_str, lowest_num_str, say_count


def get_num_as_pow(num: float) -> str:
    whole_fraction = 4 if num < 0 else 3
    return f'{str(num)[:whole_fraction]} * 10^{len(str(num)) - whole_fraction}'


async def get_say_statistics(message: Message):
    highest, lowest, say_count = get_say_numbers()
    await message.bot.send_message(
        text=f'Say stats:\ncount — {say_count}\nlowest — {lowest}\nhighest — {highest}',
        chat_id=test_group_id,
    )


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
    dp.register_message_handler(say_to_ls, commands=['message'], chat_id=test_group_id)
    dp.register_message_handler(add_paste, commands=['add'], chat_id=test_group_id)
    dp.register_message_handler(nice_pfp_counter, commands=['nice_pfp', 'nice_ava'], chat_id=test_group_id)
    dp.register_message_handler(get_similar_nice_pfp, commands=['get_similar_pfp'], chat_id=test_group_id)
    dp.register_message_handler(help, commands=['help', 'commands'], chat_id=test_group_id)
