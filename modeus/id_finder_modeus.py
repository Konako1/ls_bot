from typing import Optional
from modeus import config
import requests

headers = {
    'authority': 'utmn.modeus.org',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ru-RU',
    'content-type': 'application/json',
    'origin': 'https://utmn.modeus.org',
    'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'x-kl-ajax-request': 'Ajax_Request',
}

json_data = {
    'sort': '+fullName',
    'size': 10,
    'page': 0,
}


async def get_json_id(fio: str, date: str) -> Optional[str]:
    json_data['fullName'] = fio
    headers['referer'] = f'https://utmn.modeus.org/schedule-calendar/my?timeZone=%22Asia%2FTyumen%22&calendar=%7B%22view%22:%22agendaWeek%22,%22date%22:%22{date}T00:00:00%22%7D'
    headers['authorization'] = config.auth
    response = requests.post('https://utmn.modeus.org/schedule-calendar-v2/api/people/persons/search', cookies=config.cookies, headers=headers, json=json_data).json()

    if '_embedded' not in response:
        return None
    if len(response['_embedded']['persons']) > 1:
        return None

    json_id = response['_embedded']['persons'][0]['id']
    return str(json_id)
