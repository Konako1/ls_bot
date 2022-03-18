import re
from datetime import timedelta, time, datetime
from typing import Union, Optional, Iterable

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.utils.exceptions import BadRequest


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


def get_poll_info(text: str) -> tuple[str, Union[str, timedelta, time, int, None]]:
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
        # clean and normalize place string
        place = " ".join(map(str.strip, (x for x in text.replace(match[0], "").split() if x)))
        if not match[1] or not match[1].isdecimal():
            real_time = _written_to_numeric_ru(match[1])
        else:
            real_time = int(match[1])
        return place, timedelta(**{arg_name: real_time})

    # Try to find smth like "в 23:59" or just "23:59"
    match = re.search(r"(?:в )?([0-9]|[01][0-9]|2[0-3]):([0-5][0-9])", text, re.I)
    if match is not None:
        # clean and normalize place string
        place = " ".join(map(str.strip, (x for x in text.replace(match[0], "").split() if x)))
        return place, time(*map(int, (match[1], match[2])))

    # Try to find smth like "в 19" or "в 19 часов"
    match = re.search(r"в ([0-9](?!\d)|[01][0-9]|2[0-3])(?: час(?:а|ов)?)?", text, re.I)
    if match is not None:
        # clean and normalize place string
        place = " ".join(map(str.strip, (x for x in text.replace(match[0], "").split() if x)))
        return place, time(int(match[1]))

    # Try to find a number in the beginning or in the end
    for word in (words[0], words[-1]):
        if word.isdecimal():
            time_word = word
    if time_word is not None:
        words.remove(time_word)
        place = " ".join(words)
        if time_word.isdecimal() and 1 <= int(time_word) <= 12:
            return place, int(time_word)
        try:
            return place, time(int(time_word))
        except ValueError:
            pass

    # Finally, it's just a text without any time
    return text, None


async def process_kto(message: Message) -> None:
    """Process /kto and /кто."""

    # Set default poll answers
    options = ("Я", "Мб я", "Не я")

    # Get reply message ID
    reply = getattr(message.reply_to_message, 'message_id', None)

    # Try to find and send Easter eggs before parsing poll format
    args = message.get_args()
    if args.lower() in ("я", "ты"):
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
    place = args
    ts = []
    t0 = ""
    while t0 is not None:
        place, t0 = get_poll_info(place)
        if t0 is not None:
            ts.append(t0)

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
        # Convert `timedelta` and `int` to `time`
        now = datetime.now()
        if isinstance(t, timedelta):
            t = (now + t).time()
        elif isinstance(t, int):
            now_hour = now.hour + 1
            if now_hour <= t or now_hour - 12 >= t:
                # now = 08:30, now_hour = 9, t = 10, expected = 10:00
                # now = 22:50, now_hour = 23, t = 10, expected = 10:00
                t = time(t)
            elif now_hour >= t >= now_hour - 12:
                # now = 12:30, now_hour = 13, t = 10, expected = 22:00
                t = time((t + 12) % 24)

        # Then if it was a `time`, or it became `time`, convert it to `str` in format "HH:MM"
        if isinstance(t, time):
            t = t.strftime("%H:%M")

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
    await bot.send_poll(
        chat_id,
        question,
        list(answers),
        is_anonymous=False,
        reply_to_message_id=reply_to_id,
        allow_sending_without_reply=True,  # just in case
    )


async def help_kto(message: Message):
    text = (
        "<b>Как использовать команду /кто?</b>\n"
        "• <i>/кто место время</i> (порядок не важен) — <i>Время. Место. Кто.</i>\n"
        "• <i>/кто текст</i> — <i>Текст. Кто.</i>\n"
        "\n"
        "<b>Форматы времени</b>\n"
        "• щас, сейчас, скоро, сегодня, завтра, утром, днём, вечером, ночью, никогда и т.д.;\n"
        "• через 5 минут, через 2 часа;\n"
        "• через пять минут, через два часа (\"через одну тысячу двести пятьдесят шесть минут\" не"
        " сработает и не надо);\n"
        "• через минуту, через час;\n"
        "• в 23:30, 11:45, в 8 часов, в 8;\n"
        "• 5, 8, 22 (сработает только в начале или конце сообщения).\n"
        "\n"
        "<b>Примеры, которые точно сработают</b>\n"
        "• /кто борщ 19\n"
        "• /кто гулять сейчас\n"
        "• /кто пойдёт гулять сейчас\n"
        "• /кто сейчас пойдёт гулять\n"
        "• /кто пойдёт сейчас гулять\n"
        "• /кто борщ через 15 минут\n"
        "• /кто смотреть кино\n"
        "• /кто настолки через два часа у Евгена\n"
        "• /кто настолки в 18:30 у Евгена\n"
        "• /кто играть 7\n"
        "• /кто жрать ёпта\n"
        "• /кто жрать епта\n"
        "\n"
        "<i>В этой команде есть несколько пасхалок :-)</i>"
    )

    await message.reply(text=text, parse_mode="HTML")


def register(dp: Dispatcher):
    dp.register_message_handler(process_kto, commands=["кто", "kto"])
    dp.register_message_handler(help_kto, commands=['format'])
