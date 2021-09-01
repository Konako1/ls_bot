from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
import asyncio
from utils.utils import message_sender
from secret_chat.config import ls_group_id, traveling_days
from aiogram import Bot
from pprint import pprint


async def get_media_title():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    if current_session:
        info = await current_session.try_get_media_properties_async()
        info_dict = {song_attr: getattr(info, song_attr) for song_attr in dir(info) if song_attr[0] != '_'}
        return info_dict['title']


async def now_playing_checker(bot: Bot, sec: int):
    previous_media = ''
    while True:
        media_title = await get_media_title()
        if media_title == traveling_days and previous_media != traveling_days:
            await message_sender(
                '@Konako1 сейчас слушает <a href="https://www.youtube.com/watch?v=Cm_MuYLI71I">Traveling Days</a>,'
                ' и вам советует.',
                ls_group_id,
                bot
            )

        previous_media = media_title
        await asyncio.sleep(sec)
