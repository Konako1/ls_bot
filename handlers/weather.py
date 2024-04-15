from datetime import datetime, timedelta
from typing import Optional

import httpx
import geocoder
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from httpx import AsyncClient, Timeout

from database import Db
from secret_chat.config import OWM_API


icon_id = {
    200: '🌧',
    201: '🌧',
    202: '🌧',
    210: '🌩',
    211: '🌩',
    212: '🌩',
    221: '🌩',
    230: '⛈',
    231: '⛈',
    232: '⛈',
    300: '🌦',
    301: '🌦',
    302: '🌦',
    310: '🌦',
    311: '🌦',
    312: '🌦',
    313: '🌦',
    314: '🌦',
    321: '🌦',
    500: '🌧',
    501: '🌧',
    502: '🌧',
    503: '🌧',
    504: '🌧',
    511: '🌧',
    521: '🌧',
    522: '🌧',
    531: '🌧',
    600: '🌨',
    601: '🌨',
    602: '🌨',
    611: '🌨',
    612: '🌨',
    613: '🌨',
    615: '🌨',
    616: '🌨',
    620: '🌨',
    621: '🌨',
    622: '🌨',
    701: '🌫',
    711: '🌫',
    721: '🌫',
    731: '🌫',
    741: '🌫',
    751: '🌫',
    761: '🌫',
    762: '🌫',
    771: '🌪',
    781: '🌪',
    800: '☀️',
    801: '🌤',
    802: '⛅️',
    803: '🌥',
    804: '☁️',
}


def weather_url_builder(weather_type: str) -> str:
    return f'https://api.openweathermap.org/data/2.5/{weather_type}'


def weather_url_builder_http(weather_type: str) -> str:
    return f'http://api.openweathermap.org/data/2.5/{weather_type}'


async def get_weather(session: AsyncClient, city: str, weather_type: str, cnt: Optional[int] = None) -> Optional[dict]:
    timeout = Timeout(10.0, read=None)
    try:
        response = await session.get(
            timeout=timeout,
            url=weather_url_builder(weather_type),
            params={
                'lang': 'ru',
                'units': "metric",
                'appid': OWM_API,
                'q': city,
                'cnt': cnt
            }
        )
    except httpx.ConnectTimeout:
        try:
            response = await session.get(
                url=weather_url_builder_http(weather_type),
                params={
                    'lang': 'ru',
                    'units': "metric",
                    'appid': OWM_API,
                    'q': city,
                    'cnt': cnt
                }
            )
        except httpx.ConnectTimeout:
            return None
    data = response.json()
    return data


def calculate_time(time_range: int, api_response: Optional[dict]):
    time_zone = api_response['city']['timezone'] / 3600  # seconds to hours
    my_local_time_zone = 5  # datetime.now() uses Tyumen time cuz server is here
    time_diff = time_range * 3 + (time_zone - my_local_time_zone)
    time = datetime.now() + timedelta(hours=time_diff)
    return time.strftime("%H:%M")


async def get_weather_message(city: str) -> str:
    session = httpx.AsyncClient()
    cnt = 4
    api_response = await get_weather(session, city, 'forecast', cnt)
    if not api_response:
        await session.aclose()
        return 'Конекшон тимеаут'
    cod = int(api_response['cod'])
    if cod // 100 != 2:
        await session.aclose()
        return 'Такого города не существует' if cod == 404 else 'Пошел нахуй'
    text = f"Погода для города <b>{api_response['city']['name']}</b>\n\n"
    for time_range in range(api_response['cnt']):
        api_data = api_response['list'][time_range]
        api_weather = api_data['weather'][0]
        if time_range == 0:
            text += '<i><b>Сейчас</b></i>'
        else:
            text += f"<i><b>В {calculate_time(time_range, api_response)}</b></i>"
        text += f"\n🌡 <b>{round(api_data['main']['temp'])}°</b>\n" \
                f"{icon_id[api_weather['id']]} {str(api_weather['description']).capitalize()}\n" \
                f"💨 <b>{round(api_data['wind']['speed'])} м/с</b>\n\n"

    await session.aclose()
    return text


async def weather(message: Message):
    city = message.get_args()
    if city == '':
        async with Db() as db:
            location = await db.get_location(message.from_user.id)
        if location is None:
            city = 'Тюмень'
        else:
            city = location[1]
    text = await get_weather_message(city)
    await message.reply(text)


def get_keyboard():
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=True)
    button = KeyboardButton("Слить все свои личные данные", request_location=True)
    no_button = KeyboardButton("Пошел нахуй!!!")
    keyboard.add(button)
    keyboard.add(no_button)
    return keyboard


async def handle_location(message: Message):
    if message.chat.type != 'private':
        return
    await message.delete()
    lat = message.location.latitude
    lon = message.location.longitude
    location = geocoder.osm(f'{lat},{lon}')
    try:
        city = location.current_result.city
    except Exception as e:
        return await message.reply('Брат я не ебу где ты')

    async with Db() as db:
        location = await db.get_location(message.from_user.id)
        if location is None:
            await db.add_location(city, message.from_user.id)
        else:
            if location[1] != city:
                await db.update_location(city, message.from_user.id)
    await message.answer('Личные данные слиты в ФСБ', reply_markup=ReplyKeyboardRemove())


async def set_geo(message: Message):
    if message.chat.type != 'private':
        await message.bot.send_message(message.from_user.id, 'Поделись геолокой, она явно не сольется в ФСБ', reply_markup=get_keyboard())
        return
    await message.reply('Поделись геолокой, она явно не сольется в ФСБ', reply_markup=get_keyboard())


def register(dp):
    dp.register_message_handler(weather, commands=['w', 'weather'])
    dp.register_message_handler(set_geo, commands=['weather_geo'])
    dp.register_message_handler(handle_location, content_types=['location'])
