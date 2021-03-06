import re
from datetime import timedelta, time, datetime, date
from typing import Union, Optional, Iterable

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.utils.exceptions import BadRequest
from aiogram.utils.markdown import quote_html

TimeT = Union[str, timedelta, time, date, None]


KEYWORDS: tuple[str, ...] = (
    "епта",
    "ёпта",
    "сейчас",
    "щас",
    "now",
    "скоро",
    "позавчера",
    "вчера",
    "сегодня",
    "завтра",
    "послезавтра",
    "утром",
    "днем",
    "днём",
    "вечером",
    "ночью",
    "никогда",
)


def _written_to_numeric_ru(t: Optional[str]) -> int:
    """Converts written numbers like `"сорок два"` to int (here, `42`)."""
    r = 0
    if t is None:
        t = ""
    words = t.split(" ")
    if len(words) == 1:
        return {
            "ноль": 0,
            "": 1,
            "один": 1,
            "два": 2,
            "три": 3,
            "четыре": 4,
            "пять": 5,
            "шесть": 6,
            "семь": 7,
            "восемь": 8,
            "девять": 9,
            "десять": 10,
            "одиннадцать": 11,
            "двенадцать": 12,
            "тринадцать": 13,
            "четырнадцать": 14,
            "пятнадцать": 15,
            "шестнадцать": 16,
            "семнадцать": 17,
            "восемнадцать": 18,
            "девятнадцать": 19,
            "двадцать": 20,
            "тридцать": 30,
            "сорок": 40,
            "пятьдесят": 50,
            "шестьдесят": 60,
            # You're doing smth unnecessary if you really want this to work
        }[t.lower()]
    for word in reversed(words):
        r += _written_to_numeric_ru(word)
    return r


def _month_name_to_int_ru(t: str) -> Optional[int]:
    return {
        "января": 1,
        "февраля": 2,
        "марта": 3,
        "апреля": 4,
        "мая": 5,
        "июня": 6,
        "июля": 7,
        "августа": 8,
        "сентября": 9,
        "октября": 10,
        "ноября": 11,
        "декабря": 12,
    }.get(t.lower())


def _clean_normalize_place(text: str, full_match: str) -> str:
    """Cleans and normalizes place string"""
    return " ".join(map(str.strip, (x for x in text.replace(full_match, "").split() if x)))


def _get_poll_info(text: str) -> tuple[str, TimeT]:
    """Parse poll and return place and time."""
    # Normalize text
    text = text.strip(' \n\t?!.,;')

    # Try to find any of keywords
    words = text.split(" ")
    time_word = None
    for word in words:
        if word.lower() in KEYWORDS:
            time_word = word
    if time_word is not None:
        words.remove(time_word)
        return " ".join(words), time_word

    # Try to find smth like "через X часов/минут" or "через час/минуту"
    match = re.search(r"через (?:(.+) )?(час(?:а|ов)?|минут[уы]?)", text, re.I)
    if match is not None:
        arg_name = {"ч": "hours", "м": "minutes"}[match[2][0]]
        place = _clean_normalize_place(text, match[0])
        if not match[1] or not match[1].isdecimal():
            real_time = _written_to_numeric_ru(match[1])
        else:
            real_time = int(match[1])
        return place, timedelta(**{arg_name: real_time})

    # Try to find smth like "в 23:59" or just "23:59"
    match = re.search(r"(?:в )?([0-9]|[01][0-9]|2[0-3]):([0-5][0-9])", text, re.I)
    if match is not None:
        place = _clean_normalize_place(text, match[0])
        return place, time(*map(int, (match[1], match[2])))

    # Try to find smth like "в 19" or "в 19 часов"
    match = re.search(r"в ([0-9](?!\d)|[01][0-9]|2[0-3])(?: час(?:а|ов)?)?", text, re.I)
    if match is not None:
        place = _clean_normalize_place(text, match[0])
        return place, time(int(match[1]))

    # Try to find short date
    match = re.search(r"([012]?[0-9]|3[01]).(0\d|1[012])(?:.(\d\d|\d{4}))?", text, re.I)
    if match is not None:
        place = _clean_normalize_place(text, match[0])
        if not match[3]:
            y = datetime.now().year
        else:
            y = int(match[3])
        return place, date(y, int(match[2]), int(match[1]))

    # Try to find long date
    match = re.search(r"([012]?[0-9]|3[01]) ([а-яА-Я]+)", text, re.I)
    if match is not None:
        month = _month_name_to_int_ru(match[2])
        if month is not None:
            # Long date found, continuing
            place = _clean_normalize_place(text, match[0])
            return place, date(datetime.now().year, month, int(match[1]))

    # Finally, it's just a text without any time
    return text, None


def get_poll_info(text: str) -> tuple[str, list[TimeT]]:
    ts = []
    t0: TimeT = ""
    while t0 is not None:
        text, t0 = _get_poll_info(text)
        if t0 is not None:
            ts.append(t0)
    return text, ts


async def process_kto(message: Message) -> None:
    """Process /kto and /кто."""

    # Set default poll answers
    options = ("Я", "Мб я", "Не я")

    # Get reply message ID
    reply = getattr(message.reply_to_message, 'message_id', None)

    # Try to find and send Easter eggs before parsing poll format
    args = message.get_args()
    if args.lower() in ("я", "ты", ""):
        return await send_poll(
            message.chat.id,
            "Я",
            None,
            message.from_user.first_name,
            ("Пидорас", "Педофил"),
            reply_to_id=reply,
        )
    if args.lower() in ("ттд", "ttd", "openttd"):
        return await send_poll(
            message.chat.id,
            args,
            None,
            message.from_user.first_name,
            ("Ахахахахахахах", "Не я"),
            reply_to_id=reply,
        )
    if args.lower() == "куда а я по съёбам":
        await message.chat.unban(message.from_user.id)
        return

    # Parse poll format
    try:
        place, ts = get_poll_info(args)
    except ValueError as e:
        await message.reply(
            f"Научись правильно писать аргументы!\n"
            f"Если не знаешь, как этим пользоваться, нажми /format\n"
            f"А сейчас, лови ошибку: <code>{e.__class__.__name__}: {quote_html(str(e))}</code>"
        )
        return

    # If "точно" is in text, remove "Мб я" option
    if place and place.startswith("точно"):
        place = place.removeprefix("точно").lstrip()
        options = ("Я", "Не я")

    # If place was not specified
    if not place:
        await message.reply('Что "кто"?\nЕсли не знаешь, как этим пользоваться, нажми /format')
        return

    # Delete original message as it's not really needed
    try:
        await message.delete()
    except BadRequest:
        pass

    # If only time was not specified, then it's a question without time
    if not ts:
        return await send_poll(
            message.chat.id,
            place,
            None,
            message.from_user.first_name,
            answers=options,
            reply_to_id=reply,
        )

    # Convert each time to its string representation
    for i, t in enumerate(ts):
        # Convert `timedelta` to `time`
        now = datetime.now()
        if isinstance(t, timedelta):
            t = (now + t).time()
        # Then if it was a `time`, or it became `time`, convert it to `str` in format "HH:MM"
        if isinstance(t, time):
            t = t.strftime("%H:%M")
        # Otherwise, if it was a `date`, convert it to `str` in format "dd.mm.YYYY"
        elif isinstance(t, date):
            t = t.strftime("%d.%m.%Y")

        # It became a `str` after these conversions, or it already was a `str`, anyway we assert it
        # just in case
        assert isinstance(t, str)

        ts[i] = t

    # Finally, send poll
    await send_poll(
        message.chat.id,
        place,
        " ".join(reversed(ts)),
        message.from_user.first_name,
        answers=options,
        reply_to_id=reply,
    )


async def send_poll(
        chat_id: int,
        place: str,
        t: Optional[str],
        sent_by: Optional[str],
        answers: Iterable[str],
        reply_to_id: Optional[int] = None,
) -> None:
    """Send poll to the chat.

    :param chat_id: Telegram chat ID to send poll to.
    :param place: Place string for the poll.
    :param t: Time string for the poll or `None` for the poll without a time.
    :param sent_by: Poll author signature or `None` for anonymous (no signature).
    :param answers: Answer options for the poll.
    :param reply_to_id: Telegram message ID in target chat to reply to or `None` not to reply.
    """
    bot = Bot.get_current()
    if place[0].islower():  # .capitalize() makes the rest of the text lowercase!
        place = place[0].upper() + place[1:]
    question = f"{place}. Кто."
    if t is not None:
        if t[0].islower():  # .capitalize() makes the rest of the text lowercase!
            t = t[0].upper() + t[1:]
        question = f"{t}. {question}"
    if sent_by is not None:
        question += f"\n\nby {sent_by}"
    try:
        await bot.send_poll(
            chat_id,
            question,
            list(answers),
            is_anonymous=False,
            reply_to_message_id=reply_to_id,
            allow_sending_without_reply=True,  # just in case
        )
    except BadRequest as e:
        await bot.send_message(
            chat_id,
            f"Не могу отправить опрос: <code>{quote_html(str(e))}</code>",
        )


def _bot_poll_filter(message: Message) -> bool:
    bot = Bot.get_current()
    reply = message.reply_to_message
    return reply is not None and reply.from_user.id == bot.id and reply.poll is not None


async def stop_kto(message: Message):
    bot = Bot.get_current()
    reply = message.reply_to_message
    if reply.poll.is_closed:
        await message.reply("Не могу остановить уже остановленный опрос")
        return
    await bot.stop_poll(message.chat.id, reply.message_id)
    await message.reply("Опрос остановлен")


async def stop_kto_fallback(message: Message):
    await message.reply("Ты забыл ответить на мой опрос!")


async def help_kto(message: Message):
    text = (
        "<b>Как использовать команду /кто?</b>\n"
        "• <i>/кто место время</i> (порядок не важен) — <i>Время. Место. Кто. (Я, Мб я, Не я)</i>\n"
        "• <i>/кто текст</i> — <i>Текст. Кто. (Я, Мб я, Не я)</i>\n"
        "• <i>/кто точно место время</i> — <i>Время. Место. Кто. (Я, Не я)</i>\n"
        "• <i>/кто точно текст</i> — <i>Текст. Кто. (Я, Не я)</i>\n"
        "\n"
        "<b>Форматы времени</b>\n"
        "• щас, сейчас, скоро, сегодня, завтра, утром, днём, вечером, ночью, никогда и т.д.;\n"
        "• через 5 минут, через 2 часа;\n"
        "• через пять минут, через два часа (\"через одну тысячу двести пятьдесят шесть минут\" не"
        " сработает и не надо);\n"
        "• через минуту, через час;\n"
        "• в 23:30, 11:45, в 8 часов, в 8;\n"
        "• 31.12, 31.12.22, 31.12.2022;\n"
        "• 31 декабря;\n"
        "\n"
        "<b>Примеры, которые точно сработают</b>\n"
        "• /кто борщ в 19\n"
        "• /кто гулять сейчас\n"
        "• /кто пойдёт гулять сейчас\n"
        "• /кто сейчас пойдёт гулять\n"
        "• /кто пойдёт сейчас гулять\n"
        "• /кто борщ через 15 минут\n"
        "• /кто смотреть кино\n"
        "• /кто настолки через два часа у Евгена\n"
        "• /кто настолки в 18:30 у Евгена\n"
        "• /кто завтра в настолки в 18:30 у Евгена\n"
        "• /кто 10 июля в настолки в 17:00 у меня\n"
        "• /кто 10.07 в настолки в 17:00 у меня\n"
        "• /кто играть в 7\n"
        "• /кто жрать ёпта\n"
        "• /кто жрать епта\n"
        "• /кто точно жрать ёпта\n"
        "\n"
        "Созданный опрос можно остановить командой /stop_poll\n"
        "\n"
        "<i>В этой команде есть несколько пасхалок :-)</i>\n"
    )

    await message.reply(text=text, parse_mode="HTML")


def register(dp: Dispatcher):
    dp.register_message_handler(process_kto, commands=["кто", "kto"])
    dp.register_message_handler(help_kto, commands=['format'])
    dp.register_message_handler(stop_kto, _bot_poll_filter, commands=['stop_poll'])
    dp.register_message_handler(stop_kto_fallback, commands=['stop_poll'])
