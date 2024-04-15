import asyncio
import datetime
from asyncio import create_task, Task
from types import TracebackType
from typing import Optional, Any

import httpx
from httpx import Response

from modeus import config


def convert_datetime(schedule: list[dict]) -> list:
    for para in schedule:
        end = datetime.datetime.fromisoformat(para['end'])
        para['end'] = end
        start = datetime.datetime.fromisoformat(para['start'])
        para['start'] = start
    return schedule


def sort_schedule(schedule: list[dict]) -> list[dict]:
    sorted_schedule = []

    latest = schedule[0]
    for para in schedule:
        if para['start'] > latest['start']:
            latest = para

    for para in schedule:
        earliest = latest
        for para2 in schedule:
            if para2 not in sorted_schedule and para2['start'] < earliest['start']:
                earliest = para2
        if earliest not in sorted_schedule:
            sorted_schedule.append(earliest)

    return sorted_schedule


class ModeusApi:
    url = 'https://api.amodeus.evgfilim1.me/v0.2/'
    failed_requests_count = 0
    session: httpx.AsyncClient
    access_token: Optional[str]
    token_updater: Task
    last_response: Response

    def __init__(self):
        self.session = httpx.AsyncClient()

    async def refresh_token(self):
        self.token_updater.cancel()
        await self.endless_token_updater()

    async def is_status_code_bad(self, status_code: int):
        if status_code in [401, 500]:
            if self.failed_requests_count < 2:
                await self.refresh_token()
                self.failed_requests_count += 1
                return True
        return False

    async def request_get(self, url: str, params: dict) -> tuple[Any, Optional[int]]:
        headers = self.headers()
        if not headers:
            return None, None
        response = await self.session.get(
            url=url,
            headers=headers,
            params=params
        )
        print(f"{response.status_code} | {url}")
        return response.json(), response.status_code

    def headers(self):
        """
        Returns authorization headers
        """
        if not self.access_token:
            return None
        return {'Authorization': f'Bearer {self.access_token}'}

    async def search_user(self, fio: str) -> Optional[dict]:
        """
        base_url + search

        :param fio: user's FIO
        :return: modeus users
        """
        user, status_code = await self.request_get(
            url=self.url + 'search',
            params={'person_name': fio}
        )
        if not status_code and not user:
            return None
        if status_code == 200:
            self.failed_requests_count = 0
            return user
        elif await self.is_status_code_bad(status_code):
            return await self.search_user(fio)

    async def get_schedule(self, user_id: str) -> Optional[list[dict]]:
        schedule, status_code = await self.request_get(
            url=f'{self.url}person/{user_id}/timetable',
            params={'to': str(datetime.datetime.now() + datetime.timedelta(days=7))}
        )
        if not schedule and not status_code:
            return None
        if status_code == 200 and len(schedule) > 0:  # нужен фикс при лен == 0: значит что у чела пар не найдено
            self.failed_requests_count = 0
            schedule_json = convert_datetime(schedule)
            return sort_schedule(schedule_json)
        elif await self.is_status_code_bad(status_code):
            return await self.get_schedule(user_id)

    async def get_access_token(self) -> (Optional[str], Response):
        """
        base_url + auth

        :return: token
        """
        auth_data = await self.session.post(
            url=self.url + 'auth/login',
            data={
                'username': config.username,
                'password': config.password
            })
        auth_data_json: dict = auth_data.json()
        print(f"{auth_data.status_code} | {self.url + 'auth/login'}")
        if auth_data.status_code == 200:
            return auth_data_json['access_token'], auth_data
        elif auth_data.status_code in [401, 500]:
            return None, auth_data
        return None, None

    async def endless_token_updater(self, delay=0):
        self.access_token = None
        if delay:
            await asyncio.sleep(delay)
            self.failed_requests_count = 0

        try:
            self.access_token, self.last_response = await self.get_access_token()
        except Exception as e:
            print(f'----------\nerror when getting access token\n----------\n{e}')
            pass
        self.token_updater = create_task(self.endless_token_updater(3600))