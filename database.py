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
            await self._conn.execute('UPDATE frames SET frame=?, datetime=? WHERE count=? ',
                                     (frame, recent_datetime, frame_data.count + 1))
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
            print(args)
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

    async def get_frames_data(self) -> list[tuple]:
        cur = await self._conn.execute('SELECT frame, count FROM frames')

        rows = await cur.fetchall()
        return rows

    async def get_last_frame(self) -> Optional[Frame]:
        cur = await self._conn.execute('SELECT frame, count, datetime FROM frames ORDER BY id DESC LIMIT 1')
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
