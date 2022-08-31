from sqlite3 import IntegrityError

import aiosqlite
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import *

# DONE TODO: get set say nums
# DONE TODO: get update sticker date, get update sticker prob, get update sticker count
# DONE TODO: get update counts (say, pigeon, nice pfp)
# DONE TODO: get update frames


@dataclass()
class StickerInfo:
    name: str
    date: datetime
    probability: int
    count: int


@dataclass()
class Statistic:
    say_count: int
    pigeon_count: int
    nice_pfp_count: int
    anek_count: int


@dataclass()
class StatType:
    say = 1
    pigeon = 2
    nice_pfp = 3
    anek = 4


@dataclass()
class Frame:
    frame: int
    datetime: float
    count: int


@dataclass()
class SilenceInfo:
    is_silenced: Optional[bool]
    title: Optional[str]


class Db:
    def __init__(self, path=Path.cwd()/'ls.db'):
        self._conn = aiosqlite.connect(path)

    async def connect(self):
        self._conn = await self._conn  # type: aiosqlite.Connection
        await self._conn.execute('CREATE TABLE IF NOT EXISTS calls(sign TEXT PRIMARY KEY NOT NULL,'
                                 'num TEXT NOT NULL)')
        await self._conn.execute('CREATE TABLE IF NOT EXISTS frames(id INTEGER PRIMARY KEY AUTOINCREMENT, '
                                 'frame INTEGER NOT NULL,'
                                 'count INTEGER NOT NULL, '
                                 'datetime FLOAT NOT NULL)')
        await self._conn.execute('CREATE TABLE IF NOT EXISTS stickers(sticker TEXT PRIMARY KEY NOT NULL,'
                                 'datetime FLOAT NOT NULL,'
                                 'probability INTEGER NOT NULL,'
                                 'count INTEGER NOT NULL)')
        await self._conn.execute('CREATE TABLE IF NOT EXISTS stat(stat INTEGER PRIMARY KEY NOT NULL,'
                                 'count INTEGER NOT NULL)')
        await self._conn.execute('CREATE TABLE IF NOT EXISTS pastes(paste TEXT PRIMARY KEY NOT NULL)')
        await self._conn.execute('CREATE TABLE IF NOT EXISTS aneks(anek_id INTEGER NOT NULL,'
                                 'user_id INTEGER NOT NULL,'
                                 'is_like INTEGER NOT NULL DEFAULT 1,'
                                 'CHECK (is_like IN (1, 0)),'
                                 'PRIMARY KEY (anek_id, user_id))')
        await self._conn.execute('CREATE TABLE IF NOT EXISTS silences(user_id INTEGER PRIMARY KEY NOT NULL,'
                                 'is_silenced INTEGER NOT NULL,'
                                 'CHECK (is_silenced IN (1, 0)))')
        await self._conn.execute('CREATE TABLE IF NOT EXISTS aneks_saves(message_id INTEGER NOT NULL,'
                                 'chat_id INTEGER NOT NULL,'
                                 'is_saved INTEGER NOT NULL,'
                                 'CHECK (is_saved in (1, 0)),'
                                 'PRIMARY KEY(message_id, chat_id))')
        await self._conn.execute('CREATE TABLE IF NOT EXISTS ping_commands('
                                 'id INTEGER PRIMARY KEY NOT NULL, chat_id INTEGER NOT NULL,'
                                 'command TEXT NOT NULL)')
        await self._conn.execute('CREATE TABLE IF NOT EXISTS ping_users(user_id INTEGER PRIMARY KEY NOT NULL,'
                                 'username TEXT NOT NULL)')
        await self._conn.execute('CREATE TABLE IF NOT EXISTS command_user('
                                 'command_id INTEGER NOT NULL REFERENCES ping_commands(id),'
                                 'user_id INTEGER NOT NULL REFERENCES ping_users(user_id),'
                                 'UNIQUE(command_id, user_id))')
        await self._conn.commit()

    async def close(self):
        await self._conn.commit()
        await self._conn.close()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        return None

    async def add_frame(self, frame: int, recent_datetime: float):
        frame_data = await self.get_frame_stat(frame)
        if frame_data is None:
            await self._conn.execute('INSERT INTO frames(frame, count, datetime) VALUES (?, ?, ?)',
                                     (frame, 1, recent_datetime))
        else:
            await self._conn.execute('UPDATE frames SET count=?, datetime=? WHERE frame=? ',
                                     (frame_data.count + 1, recent_datetime, frame))
        await self._conn.commit()

    async def add_sticker(self, sticker: StickerInfo):
        await self._conn.execute('INSERT INTO stickers(sticker, datetime, probability, count) VALUES(?, ?, ?, ?)',
                                 (sticker.name, sticker.date.timestamp(), sticker.probability, 0))
        await self._conn.commit()

    async def add_paste(self, text: str):
        if text is None:
            return False
        await self._conn.execute('INSERT INTO pastes(paste) VALUES (?)',
                                 (text, ))
        await self._conn.commit()

    async def add_devil_trigger(self, file_id: str) -> bool:
        if file_id is None:
            return False
        await self._conn.execute('INSERT INTO devil_triggers(file_id) VALUES (?)',
                                 (file_id, ))
        await self._conn.commit()
        return True

    async def add_user_in_silences(self, user_id: int, is_silence_int: int, title: str):
        if user_id is None:
            return False
        await self._conn.execute('INSERT INTO silences(user_id, is_silenced, title) VALUES (?, ?, ?)',
                                 (user_id, is_silence_int, title))
        await self._conn.commit()
        return True

    async def add_message_to_saves(self, message_id: int, chat_id: int):
        await self._conn.execute('INSERT INTO aneks_saves(message_id, chat_id, is_saved) VALUES(?, ?, ?)',
                                 (message_id, chat_id, 0))
        await self._conn.commit()

    async def add_ping_command(self, chat_id: int, command: str):
        await self._conn.execute('INSERT INTO ping_commands(chat_id, command) VALUES(?, ?)',
                                 (chat_id, command))
        await self._conn.commit()

    async def add_ping_user(self, user_id: int, username: str):
        await self._conn.execute('INSERT INTO ping_users(user_id, username) VALUES(?, ?)'
                                 'ON CONFLICT(user_id) DO UPDATE SET username=?',
                                 (user_id, username, username))
        await self._conn.commit()

    async def bind_command_user(self, user_id: int, command_id: int) -> bool:
        try:
            await self._conn.execute('INSERT INTO command_user(command_id, user_id) VALUES(?, ?)',
                                     (command_id, user_id))
        except IntegrityError:
            return False
        await self._conn.commit()

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
        await self._conn.commit()

    async def update_sticker(self, sticker: StickerInfo):
        previous_sticker = await self.get_sticker_info(sticker.name)

        if previous_sticker is None:
            args = (sticker.name, sticker.date.timestamp(), sticker.probability, sticker.count)
            await self._conn.execute('INSERT INTO stickers(sticker, datetime, probability, count) VALUES (?, ?, ?, ?)',
                                     args)
        else:
            await self._conn.execute('UPDATE stickers SET datetime=?, probability=?, count=? WHERE sticker=?',
                                     (sticker.date.timestamp(), sticker.probability, previous_sticker.count + 1, sticker.name))
        await self._conn.commit()

    async def update_stat(self, stat_type: int):
        stat_count = await self.get_statistics(stat_type)

        if stat_count is None:
            await self._conn.execute('INSERT INTO stat(stat, count) VALUES (?, ?)',
                                     (stat_type, 1))
        else:
            await self._conn.execute('UPDATE stat SET count=? WHERE stat=?',
                                     (stat_count + 1, stat_type))
        await self._conn.commit()

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
        await self._conn.commit()

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

    async def get_frames_data(self) -> Optional[list[tuple]]:
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

    async def get_all_ping_commands(self, chat_id: int) -> list[tuple[str]]:
        cur = await self._conn.execute('SELECT command FROM ping_commands WHERE chat_id=?',
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
