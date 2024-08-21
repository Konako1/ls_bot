import asyncio
import json
from datetime import datetime

from database.db import Db


async def migrate_frames():
    with open('json/frames.json', 'r') as f:
        data = json.load(f)

    frames: dict[str, int] = data['frames']

    async with Db() as db:
        for frame in frames:
            for i in range(frames[frame]):
                await db.add_frame(frame, datetime.now())
    print('Done')


if __name__ == '__main__':
    asyncio.run(migrate_frames())
