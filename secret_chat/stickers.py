from datetime import datetime

from secret_chat.config import json_path
import json


class Stickers:
    def __init__(self):
        self._stickers_storage = {}
        self.stickers_load()

    def stickers_load(self):
        try:
            with open(json_path + 'stickers.json', encoding='utf8') as f:
                self._stickers_storage = json.load(f)
        except FileExistsError:
            pass

    def save_data(self):
        with open(json_path + 'stickers.json', 'w', encoding='utf8') as f:
            json.dump(self._stickers_storage, f, ensure_ascii=False)

    def update_bear_values(self, date: datetime, prob: int):
        self._stickers_storage["bear"]["bear_date"] = date.timestamp()
        self._stickers_storage["bear"]['bear_prob'] = prob
        self.save_data()

    def get_bear_values(self) -> tuple[datetime, int]:
        date = datetime.fromtimestamp(self._stickers_storage["bear"]["bear_date"])
        prob = self._stickers_storage["bear"]["bear_prob"]
        return date, prob
