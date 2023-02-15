from typing import Optional
from modeus import config
from modeus.id_finder_modeus import get_json_id
import requests
import datetime

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
    'size': 500,
    'timeMin': '2023-02-13T00:00:00+05:00',
    'timeMax': '2023-02-19T23:59:59+05:00',
    'attendeePersonId': [
        '05f08994-60bb-431f-9a8a-e3fd4b35ae0b',
    ],
}


async def get_schedule(fio: Optional[str], modeus_id: Optional[str], date: str) -> Optional[list[dict]]:
    if fio is not None and modeus_id is None:
        modeus_id = await get_json_id(fio, date)
        if modeus_id is None:
            return None
        json_data['attendeePersonId'] = [modeus_id]
    elif fio is None and modeus_id is not None:
        json_data['attendeePersonId'] = [modeus_id]
    else:
        raise AttributeError(f'fio: {fio}, modeus_id: {modeus_id}')

    headers['referer'] = f'https://utmn.modeus.org/schedule-calendar/mobile?timeZone=%22Asia%2FTyumen%22&calendar=%7B%22view%22:%22agendaWeek%22,%22date%22:%22{date}%22%7D'
    headers['authorization'] = config.auth

    r = requests.post(
        'https://utmn.modeus.org/schedule-calendar-v2/api/calendar/events/search?tz=Asia/Tyumen&authAction=',
        cookies=config.cookies,
        headers=headers,
        json=json_data
    )
    response = r.json()

    paras = []
    # проход по всем парам
    for lession in response['_embedded']['events']:
        event_id = lession['id'] # айди ивента зантия
        name = lession['name'] # тема пары
        course_name_id = lession['_links']['course-unit-realization']['href'].split('/')[1]

        # поиск названия предмета
        course_name_short = ''
        course_name = ''
        for course in response['_embedded']['course-unit-realizations']:
            if course_name_id == course['id']:
                course_name = course['name']
                course_name_short = course['nameShort']

        # время начала и конца пар
        start_time = datetime.datetime.fromisoformat(lession['startsAtLocal'])
        end_time = datetime.datetime.fromisoformat(lession['endsAtLocal'])

        # поиск аудитории
        room = ''
        for event_location in response['_embedded']['event-locations']:
            if event_id == event_location['eventId']:
                try:
                    event_locations_href = event_location['_links']['event-rooms']['href'].split('/')[1]
                except KeyError:
                    # print('Пара: Физра ебаная'.ljust(90, ' ') + 'Аудитория: помойка')
                    room = event_location['customLocation']
                    break
                for event_room in response['_embedded']['event-rooms']:
                    if event_locations_href == event_room['id']:
                        event_rooms_href = event_room['_links']['room']['href'].split('/')[1]
                        for rooms in response['_embedded']['rooms']:
                            if event_rooms_href == rooms['id']:
                                room = rooms['name']

        paras.append(
            {'short_name': course_name_short,
             'name': course_name,
             'room': room,
             'start_time': start_time,
             'end_time': end_time}
        )

    p_sorted = []

    latest = paras[0]
    for para in paras:
        if para['start_time'] > latest['start_time']:
            latest = para

    for para in paras:
        earliest = latest
        for para2 in paras:
            if para2 not in p_sorted and para2['start_time'] < earliest['start_time']:
                earliest = para2
        if earliest not in p_sorted:
            p_sorted.append(earliest)

    return p_sorted
