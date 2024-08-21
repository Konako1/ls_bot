from database.class_models import Mashup
from database.db import Db


class MashupModel(Db):
    def __init__(self):
        self._model = 'mashup_posts'
        super().__init__(self._model)
        self._id = None
        self._post_link = None
        self._song_name = None
        self._like_count = None
        self._view_count = None

    async def add_post(self, mashup: Mashup):
        #TODO: проверка на существование по post_link
        await self.insert(
            post_link=mashup.post_link,
            song_name=mashup.song_name,
            like_count=mashup.like_count,
            view_count=mashup.view_count
        )