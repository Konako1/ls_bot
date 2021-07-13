from secret_chat.config import path
import json
from datetime import datetime


class Frames:
    def __init__(self):
        self._frames_storage = {}
        self.frames_load()

    def frames_load(self):
        try:
            with open(path + 'frames.json', encoding='utf8') as f:
                self._frames_storage = json.load(f)
        except FileExistsError:
            pass

    def save_frames(self):
        with open(path + 'frames.json', 'w', encoding='utf8') as f:
            json.dump(self._frames_storage, f, ensure_ascii=False, )

    def save_frame(self, frame: int):
        value = self._frames_storage.get(str(frame), 0)
        self._frames_storage[str(frame)] = value + 1
        self.save_frames()

    def get_nicest_frame(self) -> tuple[list, int]:
        value = 0
        frames = list()
        for k, v in self._frames_storage["frames"].items():
            if v == value:
                frames.append(k)
            if v > value:
                frames.clear()
                frames.append(k)
                value = v
        return frames, value

    def get_datetime(self) -> datetime:
        return datetime.fromtimestamp(self._frames_storage['nice_ava_datetime'])

    def set_datetime(self, date: datetime):
        self._frames_storage['nice_ava_datetime'] = date.timestamp()
        self.save_frames()
