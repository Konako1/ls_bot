import httpx
from pprint import pprint
from secret_chat.config import VK_TOKEN
from dataclasses import dataclass

akb_group = -149279263
BASE_URL = 'https://api.vk.com/method'
wall_get = 'wall.get'


@dataclass()
class RequestParams:
    method: str
    group_id: int
    post_count: int
    offset: int


def url_builder(
        method: str,
) -> str:
    return f'{BASE_URL}/{method}'


class Vk:
    def __init__(self):
        self._session = httpx.AsyncClient()
        self._token = VK_TOKEN
        self._akb_post_count = 0

    async def api_request(
            self,
            http_method: str,
            params: RequestParams,
    ) -> dict:
        url = url_builder(params.method)
        if http_method == 'GET':
            response = await self._session.get(
                url,
                params={
                    'v': '5.52',
                    'access_token': VK_TOKEN,
                    'owner_id': params.group_id,
                    'count': params.post_count,
                    'offset': params.offset
                }
            )
        else:
            raise NotImplemented
        response.raise_for_status()
        return response.json()

    async def get_funny(
            self,
            group_id: int,
            funny_count: int,
            offset: int
    ) -> list:
        params = RequestParams(
            method=wall_get,
            group_id=group_id,
            post_count=funny_count,
            offset=offset,
        )
        response = await self.api_request('GET', params)
        funny = self.edit_funny_response(response)
        return funny

    def edit_funny_response(
            self,
            funny: dict,
    ) -> list[str]:
        funny_list = []
        actual_response = funny['response']['items']
        for post in actual_response:
            try:
                attachments = post['attachments']
            except KeyError:
                attachments = False
            if post['marked_as_ads'] == 1 or post['text'] == '' or attachments:
                continue
            funny_list.append(post['text'])
        return funny_list

    async def get_wall_post_count(
            self,
            group_id: int,
    ) -> int:
        params = RequestParams(
            method=wall_get,
            post_count=0,
            group_id=group_id,
            offset=0,
        )
        request = await self.api_request('GET', params)
        return request['response']['count']

    async def get_akb_post_count(
            self
    ):
        if self._akb_post_count == 0:
            self._akb_post_count = await self.get_wall_post_count(akb_group)
        return self._akb_post_count

    async def close(self):
        await self._session.aclose()
