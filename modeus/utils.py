from datetime import datetime
from typing import Optional

from aiogram.types import Message

from database import Db
from modeus.modeus_api import ModeusApi

event_types = {
    'LECT': '💚 Лекция 💚',
    'SEMI': '💙 Практика 💙',
    'LAB':  '🧡 Лаба 🧡',
    'CONS': '💜 Консультация 💜',
    'PRETEST': '❗️ Зачет ❗️',
    'EXAMINATION': '‼️ Экзамен ‼️'
}

acronyms = {
    '3': 'ИнЗем',
    '4': 'ФЭИ',
    '5': 'ИМиКН',
    '6': 'ИнБио',
    '7': 'Олимпия',
    '9': 'СОК',
    '10': 'ИГИП',
    '11': 'СоцГум',
    '12': 'ЕД',
    'ЦЗВС — ул. Барнаульская,41': 'Экопарк',
    '16': 'ИПИП',
    '17': 'Приемная Комиссия',
    '19': 'ШПИ',
    'Microsoft Teams': 'Teams',
    '': '',
}


weekdays = {
    "пн": 0,
    "вт": 1,
    "ср": 2,
    "чт": 3,
    "пт": 4,
    "сб": 5,
    "вс": 6,
    'mon': 0,
    'tue': 1,
    'wed': 2,
    'thu': 3,
    'fri': 4,
    'sat': 5,
    'sun': 6
}


weekdays_reverse = {
    0: "пн",
    1: "вт",
    2: "ср",
    3: "чт",
    4: "пт",
    5: "сб",
    6: "вс",
}


def days_calc(date: datetime) -> int:
    now = datetime.now().date()
    delta = date - now
    return delta.days


def naturaldate(date: datetime.date) -> str:
    days = days_calc(date)
    weekday = datetime.now().weekday() + days
    weekday = weekday if weekday < 7 else weekday - 7
    weekday_word = weekdays_reverse[weekday]

    if days == 0:
        return f'Сегодня ({weekday_word})'
    elif days == 1:
        return f'Завтра ({weekday_word})'

    word = ''
    if days % 100 in [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]:
        word = 'дней'
    elif days % 10 in [2, 3, 4]:
        word = 'дня'
    elif days % 10 in [1]:
        word = 'день'
    return f'Через {days} {word} ({weekday_word})'


def user_filter(users: dict) -> Optional[str]:
    if len(users) == 0:
        return 'Введи корректное ФИО'
    if len(users) > 1:
        return f'Найдено пользователей: {len(users)}. Уточни ФИО'
    return None


async def fc_filter(user_id: int, events: list[dict]) -> list[dict]:
    async with Db() as db:
        is_fc = bool(await db.get_modeus_fc_toggle(user_id))

    result = []
    for event in events:
        # исключаем физру из выдачи при отключенной физре
        if not is_fc and event['location']['full'] == 'ЦЗВС — ул. Барнаульская,41':
            continue
        result.append(event)

    return result


def day_fio_split(args: str) -> tuple[str, float]:
    weekday_now = datetime.now().weekday()
    if args != '' and args.split()[-1].lower() in weekdays.keys():
        if len(args.split()) == 1:
            weekday_word = args
            fio = ''
        else:
            fio, weekday_word = args.rsplit(maxsplit=1)
        weekday = weekdays[weekday_word]
        if weekday_now >= weekday:
            append_days = weekday + 7 - weekday_now
        else:
            append_days = weekday - weekday_now
    elif '+' in args:
        fio, append_days = args.split('+', 1)
    elif '-' in args:
        splitted = args.split('-', 1)
        fio = splitted[0]
        append_days = float(splitted[1]) * -1
    else:
        fio = args
        append_days = 0
    return fio, float(append_days)


async def prepare_request(message: Message, modeus_api: ModeusApi, _fio: str) -> tuple[bool, str]:
    fio = None if _fio == '' else _fio

    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        user_id = message.from_user.id
    if fio is None:
        async with Db() as db:
            modeus_id = await db.get_modeus_id(user_id)
            if modeus_id is None:
                if message.reply_to_message:
                    return False, 'Чел не сохранял свои ФИО'
                return False, 'Либо впиши ФИО, либо /save_modeus_fio + ФИО'
    else:
        modeus_users = await modeus_api.search_user(fio)
        user_text = user_filter(modeus_users)
        if user_text is not None:
            return False, user_text
        modeus_id = modeus_users[0]['id']
    return True, modeus_id


def format_event_final_text(next_event: dict) -> str:
    building = next_event["location"]['full'] if next_event["location"]['building'] is None else next_event["location"]['building']['number']
    acronym = acronyms[str(building)]
    text = f'{format_event_type(next_event["lesson"])}\n' \
           f'<b><u>{next_event["lesson"]["subject"]["name_short"]}</u></b>\n\n' \
           f'🕑 <b>{next_event["start"].strftime("%H:%M")}-{next_event["end"].strftime("%H:%M")}</b> | {naturaldate(next_event["start"].date())}\n' \
           f'♿️ {"<b>" + next_event["location"]["room"] + "</b> | " if next_event["location"]["room"] is not None else ""}{acronym}'
    return text


def format_event_type(lesson: dict) -> str:
    if lesson['type'] in event_types.keys():
        return event_types[lesson['type']]
    if lesson['format'] in event_types.keys():
        return event_types[lesson['format']]
    return '⁉️ Какая-то хуйня ⁉️'
