import json
import random
from secret_chat.config import json_path


class PasteUpdater:
    def __init__(self):
        self._storage = []
        self.load()

    def load(self):
        try:
            with open(json_path + 'pastes.json', encoding='utf8') as f:
                self._storage = json.load(f)
        except FileExistsError:
            pass

    def save(self):
        with open(json_path + "pastes.json", 'w', encoding='utf8') as f:
            json.dump(self._storage, f, indent=4, ensure_ascii=False, )

    def add_paste(self, text: str):
        self._storage.append(text)
        self.save()

    def get_random_paste(self) -> str:
        return random.choice(self._storage)

    def __len__(self) -> int:
        return len(self._storage)
