from typing import Any

from aiogram.dispatcher.middlewares import BaseMiddleware

from modeus.modeus_api import ModeusApi


class ModeusMiddleware(BaseMiddleware):
    def __init__(self, modeus_api: ModeusApi):
        self._modeus_api = modeus_api
        super().__init__()

    async def on_process_message(self, _, data: dict[str, Any]):
        data['modeus_api'] = self._modeus_api
