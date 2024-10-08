import random
import string
from sqlite3 import IntegrityError
import secrets

import aiosqlite
from typing import Optional
from datetime import datetime
from pathlib import *

from database.class_models import StickerInfo, Frame, SilenceInfo

# DONE TODO: get set say nums
# DONE TODO: get update sticker date, get update sticker prob, get update sticker count
# DONE TODO: get update counts (say, pigeon, nice pfp)
# DONE TODO: get update frames


connection = Path.cwd()/'ls.db'


class Db:
    def __init__(self, model: str = None):
        self._model = model
        self._sql = ''
        self._parameters = {}
        self._conn = aiosqlite.connect(connection)

    async def connect(self):
        self._conn = await self._conn  # type: aiosqlite.Connection

    async def close(self):
        await self._conn.commit()
        await self._conn.close()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        return None

    def _convert_to_string(self, values: list) -> str:
        result = ''
        for item in values:
            result += str(item) + ', '
        return result.rstrip(', ')

    def _question_mark_string(self, count: int) -> str:
        result = ''
        for item in range(count):
            result += '?, '
        return result.rstrip(', ')

    def _parametrized_string(self, items: dict) -> str:
        result = ''
        for key, value in items.items():
            rnd_value = ''.join(random.sample(string.ascii_lowercase, 8))
            self._parameters[rnd_value] = value
            result += f'{key}=:{rnd_value}, '
        return result.rstrip(', ')

    async def insert(self, **values):
        self._sql = f'INSERT INTO {self._model} ({self._convert_to_string(list(values.keys()))}) VALUES ({self._question_mark_string(len(values))})'
        await self._conn.execute(self._sql, list(values.values()))

    async def update(self, **values):
        self._sql = f'UPDATE {self._model} SET {self._parametrized_string(values)} ' + self._sql
        await self._conn.execute(self._sql, self._parameters)

    async def get(self, *fields):
        fields_str = '*'
        if fields is not None:
            fields_str = self._convert_to_string(list(fields))
        self._sql = f'SELECT {fields_str} FROM {self._model} ' + self._sql

    def where(self, **values):
        self._sql += f' WHERE {self._parametrized_string(values)} '
        return self

    async def add_frame(self, frame: int, recent_datetime: float):
        frame_data = await self.get_frame_stat(frame)
        if frame_data is None:
            await self._conn.execute('INSERT INTO frames(frame, count, datetime) VALUES (?, ?, ?)',
                                     (frame, 1, recent_datetime))
        else:
            await self._conn.execute('UPDATE frames SET count=?, datetime=? WHERE frame=? ',
                                     (frame_data.count + 1, recent_datetime, frame))

    async def add_sticker(self, sticker: StickerInfo):
        await self._conn.execute('INSERT INTO stickers(sticker, datetime, probability, count) VALUES(?, ?, ?, ?)',
                                 (sticker.name, sticker.date.timestamp(), sticker.probability, 0))

    async def add_paste(self, text: str):
        if text is None:
            return False
        await self._conn.execute('INSERT INTO pastes(paste) VALUES (?)',
                                 (text, ))

    async def add_devil_trigger(self, file_id: str) -> bool:
        if file_id is None:
            return False
        await self._conn.execute('INSERT INTO devil_triggers(file_id) VALUES (?)',
                                 (file_id, ))
        return True

    async def add_user_in_silences(self, user_id: int, is_silence_int: int, title: str):
        if user_id is None:
            return False
        await self._conn.execute('INSERT INTO silences(user_id, is_silenced, title) VALUES (?, ?, ?)',
                                 (user_id, is_silence_int, title))
        return True

    async def add_message_to_saves(self, message_id: int, chat_id: int):
        await self._conn.execute('INSERT INTO aneks_saves(message_id, chat_id, is_saved) VALUES(?, ?, ?)',
                                 (message_id, chat_id, 0))

    async def add_ping_command(self, chat_id: int, command: str):
        await self._conn.execute('INSERT INTO ping_commands(chat_id, command) VALUES(?, ?)',
                                 (chat_id, command))

    async def add_ping_user(self, user_id: int, username: str):
        await self._conn.execute('INSERT INTO ping_users(user_id, username) VALUES(?, ?)'
                                 'ON CONFLICT(user_id) DO UPDATE SET username=?',
                                 (user_id, username, username))

    async def add_modeus_user(self, user_id: int, modeus_id: str):
        await self._conn.execute('INSERT INTO modeus(user_id, modeus_id) VALUES(?, ?)'
                                 'ON CONFLICT(user_id) DO UPDATE SET modeus_id=?',
                                 (user_id, modeus_id, modeus_id))

    async def bind_command_user(self, user_id: int, command_id: int) -> bool:
        try:
            await self._conn.execute('INSERT INTO command_user(command_id, user_id) VALUES(?, ?)',
                                     (command_id, user_id))
        except IntegrityError:
            return False

    async def update_num(self, num: float):
        sign = 'positive' if num > 0 else 'negative'
        saved_num = await self.get_num(sign)

        if saved_num is None:
            await self._conn.execute('INSERT INTO calls(sign, num) VALUES (?, ?)',
                                     (sign, num))
        else:
            if sign == 'positive':
                num_to_save = num if num > saved_num else saved_num
            else:
                num_to_save = num if num < saved_num else saved_num
            await self._conn.execute('UPDATE calls SET num=? WHERE sign=?',
                                     (str(num_to_save), sign))

    async def update_sticker(self, sticker: StickerInfo):
        previous_sticker = await self.get_sticker_info(sticker.name)

        if previous_sticker is None:
            args = (sticker.name, sticker.date.timestamp(), sticker.probability, sticker.count)
            await self._conn.execute('INSERT INTO stickers(sticker, datetime, probability, count) VALUES (?, ?, ?, ?)',
                                     args)
        else:
            await self._conn.execute('UPDATE stickers SET datetime=?, probability=?, count=? WHERE sticker=?',
                                     (sticker.date.timestamp(), sticker.probability, previous_sticker.count + 1, sticker.name))

    async def update_stat(self, stat_type: int):
        stat_count = await self.get_statistics(stat_type)

        if stat_count is None:
            await self._conn.execute('INSERT INTO stat(stat, count) VALUES (?, ?)',
                                     (stat_type, 1))
        else:
            await self._conn.execute('UPDATE stat SET count=? WHERE stat=?',
                                     (stat_count + 1, stat_type))

    async def update_anek_data(self, anek_id: int, user_id: int, is_like: bool) -> bool:
        is_like = 1 if is_like else 0
        saved_is_like = await self.get_user_answer_for_anek(user_id, anek_id)

        if saved_is_like is None:
            await self._conn.execute('INSERT INTO aneks(anek_id, user_id, is_like) VALUES (?,?,?)',
                                     (anek_id, user_id, is_like))
            return False
        await self._conn.execute('UPDATE aneks SET is_like=? WHERE user_id=? AND anek_id=?',
                                 (is_like, user_id, anek_id,))
        return True

    async def update_silences(self, user_id: int, is_silence: bool, title: str) -> Optional[bool]:
        is_silence_int = 1 if is_silence is True else 0
        await self._conn.execute('UPDATE silences SET is_silenced=?, title=? WHERE user_id=?',
                                 (is_silence_int, title, user_id, ))
        return True

    async def update_message_to_save(self, message_id: int, chat_id: int):
        await self._conn.execute('UPDATE aneks_saves SET is_saved=? WHERE message_id=? AND chat_id=?',
                                 (1, message_id, chat_id))

    async def update_modeus_fc_toggle(self, user_id: int, modeus_id: str, toggle: int):
        await self._conn.execute('UPDATE modeus SET fc_toggle=? WHERE user_id=? AND modeus_id=?',
                                 (toggle, user_id, modeus_id))

    async def get_frame_stat(self, frame: int) -> Optional[Frame]:
        cur = await self._conn.execute('SELECT count, datetime FROM frames WHERE frame=?',
                                       (frame, ))
        row = await cur.fetchone()
        if row is not None:
            return Frame(
                frame=frame,
                count=row[0],
                datetime=row[1],
            )
        return None

    async def get_frames_data(self) -> Optional[list[(int, int)]]:
        cur = await self._conn.execute('SELECT frame, count FROM frames')

        rows = await cur.fetchall()
        return rows

    async def get_last_frame(self) -> Optional[Frame]:
        cur = await self._conn.execute('SELECT frame, count, datetime FROM frames ORDER BY datetime DESC LIMIT 1')
        row = await cur.fetchone()
        if row is not None:
            return Frame(
                frame=row[0],
                count=row[1],
                datetime=row[2],
            )
        return None

    async def get_paste(self, offset: int, limit: int = 1) -> Optional[str]:
        cur = await self._conn.execute('SELECT paste FROM pastes LIMIT ? OFFSET ?',
                                       (limit, offset))
        row = await cur.fetchone()
        if row is not None:
            return row[0]
        return None

    async def get_paste_count(self) -> Optional[int]:
        cur = await self._conn.execute('SELECT COUNT(*) FROM pastes')
        row = await cur.fetchone()
        if row is not None:
            return row[0]
        return None

    async def get_num(self, sign: str) -> Optional[float]:
        cur = await self._conn.execute('SELECT num FROM calls WHERE sign=?',
                                       (sign, ))
        row = await cur.fetchone()
        if row is not None:
            return float(row[0])
        return None

    async def get_sticker_info(self, sticker: str) -> Optional[StickerInfo]:
        cur = await self._conn.execute('SELECT datetime, probability, count FROM stickers WHERE sticker=?',
                                       (sticker, ))
        row = await cur.fetchone()
        if row is not None:
            return StickerInfo(sticker, datetime.fromtimestamp(row[0]), int(row[1]), int(row[2]))
        return None

    async def get_statistics(self, stat: int) -> Optional[int]:
        cur = await self._conn.execute('SELECT count FROM stat WHERE stat=?',
                                       (stat, ))
        row = await cur.fetchone()
        if row is not None:
            return row[0]
        return None

    async def get_user_answer_for_anek(self, user_id: int, anek_id: int) -> Optional[bool]:
        cur = await self._conn.execute('SELECT is_like FROM aneks WHERE user_id=? AND anek_id=?',
                                       (user_id, anek_id))
        row = await cur.fetchone()
        if row is None:
            return None
        if int(row[0]) == 1:
            return True
        return False

    async def get_anek_data(self, anek_id: int) -> Optional[list[tuple]]:
        cur = await self._conn.execute('SELECT is_like FROM aneks WHERE anek_id=?',
                                       (anek_id,))
        rows = await cur.fetchall()
        return rows

    async def get_ping_command_id(self, chat_id: int, command: str) -> int:
        cur = await self._conn.execute('SELECT id FROM ping_commands WHERE chat_id=? AND command=?',
                                       (chat_id, command))
        row = await cur.fetchone()
        if row is not None:
            return int(row[0])
        return -1

    async def get_all_ping_usernames(self, command_id: int) -> list[tuple[str]]:
        cur = await self._conn.execute('SELECT u.username FROM command_user AS cu INNER JOIN ping_users AS u ON u.user_id = cu.user_id WHERE cu.command_id = ?',
                                       (command_id, ))
        rows = await cur.fetchall()
        return rows

    async def get_all_ping_commands(self, chat_id: int) -> list[tuple[str, int]]:
        cur = await self._conn.execute('SELECT command, id FROM ping_commands WHERE chat_id=?',
                                       (chat_id, ))
        rows = await cur.fetchall()
        return rows

    async def get_all_ping_commands_for_user(self, chat_id: int, user_id: int) -> list[int]:
        cur = await self._conn.execute('SELECT id, command FROM ping_commands WHERE chat_id=?',
                                       (chat_id, ))
        all_chat_commands_id = await cur.fetchall()
        cur_ = await self._conn.execute('SELECT command_id FROM command_user WHERE user_id=?',
                                        (user_id, ))
        user_commands_id = await cur_.fetchall()
        user_commands_id_list = map(lambda x: x[0], user_commands_id)
        result: list[int] = []
        for command_id, command in all_chat_commands_id:
            if command_id in user_commands_id_list:
                result.append(command)
        return result

    async def get_modeus_id(self, user_id: int) -> Optional[str]:
        cur = await self._conn.execute('SELECT modeus_id FROM modeus WHERE user_id=?',
                                       (user_id,))
        row = await cur.fetchone()
        if row is not None:
            return row[0]
        return None

    async def get_modeus_fc_toggle(self, user_id: int) -> Optional[str]:
        cur = await self._conn.execute('SELECT fc_toggle FROM modeus WHERE user_id=?',
                                       (user_id,))
        row = await cur.fetchone()
        if row is not None:
            return row[0]
        return None

    async def remove_frame(self, frame: int) -> Optional[bool]:
        cur = await self._conn.execute('SELECT count FROM frames WHERE frame=?',
                                       (frame, ))
        row = await cur.fetchone()
        if row is None:
            return None
        if int(row[0]) == 1:
            await self._conn.execute('DELETE FROM frames WHERE frame=?',
                                     (frame, ))
            return True
        if int(row[0]) > 1:
            await self._conn.execute('UPDATE frames SET count=?, datetime=? WHERE frame=?',
                                     (row[0] - 1, 0.0, frame, ))
            return True

    async def remove_user_from_command(self, command_id: int, user_id: int) -> bool:
        cur = await self._conn.execute('DELETE FROM command_user WHERE command_id=? AND user_id=?',
                                       (command_id, user_id))
        row = cur.fetchone()
        if row is None:
            return False
        return True

    async def remove_command(self, command_id):
        await self._conn.execute('DELETE FROM ping_commands WHERE id=?',
                                 (command_id, ))
        await self._conn.execute('DELETE FROM command_user WHERE command_id=?',
                                 (command_id, ))

    async def get_all_devil_triggers(self) -> list[tuple[str]]:
        cur = await self._conn.execute('SELECT file_id FROM devil_triggers')
        rows = await cur.fetchall()
        return rows

    async def get_user_silence_info(self, user_id: int) -> SilenceInfo:
        cur = await self._conn.execute('SELECT is_silenced, title FROM silences WHERE user_id=?',
                                       (user_id, ))
        row = await cur.fetchone()
        if row is None:
            return SilenceInfo(None, None)
        if str(row[0]) == '1':
            return SilenceInfo(
                is_silenced=True,
                title=str(row[1])
            )
        else:
            return SilenceInfo(
                is_silenced=False,
                title=str(row[1])
            )

    async def get_is_message_to_save(self, message_id: int, chat_id: int) -> Optional[bool]:
        cur = await self._conn.execute('SELECT is_saved FROM aneks_saves WHERE message_id=? AND chat_id=?',
                                       (message_id, chat_id))
        row = await cur.fetchone()
        if row is not None:
            is_saved = True if int(row[0]) == 1 else False
            return is_saved
        return None

    async def add_wysi(self, regnum: str, region: Optional[int]):
        await self._conn.execute('INSERT INTO wysi(regnum, region, date_created) VALUES (?, ?, CURRENT_TIMESTAMP)',
                                 (regnum, region))

    async def update_wysi(self, id: int, regnum: str, region: Optional[int]):
        await self._conn.execute('UPDATE wysi SET  regnum=?, region=? WHERE id=?',
                                 (regnum, region, id))

    async def get_wysi(self) -> list[tuple[str]]:
        cur = await self._conn.execute('SELECT * FROM wysi')
        return await cur.fetchall()

    async def delete_wysi(self, id: int):
        await self._conn.execute('DELETE FROM wysi WHERE id=?', (id, ))

    async def add_location(self, city: str, user_id: int):
        await self._conn.execute('INSERT INTO locations(city, user_id) VALUES (?, ?)',
                                 (city, user_id))

    async def update_location(self, city: str, user_id: int):
        await self._conn.execute('UPDATE locations SET city=? WHERE user_id=?',
                                 (city, user_id))

    async def get_location(self, user_id: int) -> Optional[tuple[int, str]]:
        cur = await self._conn.execute('SELECT id, city FROM locations WHERE user_id=?',
                                       (user_id,))
        row = await cur.fetchone()
        return row

    async def delete_location(self, id: int):
        await self._conn.execute('DELETE FROM locations WHERE id=?', (id, ))


