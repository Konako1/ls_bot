from datetime import datetime, timedelta
from typing import Optional

import httpx
from aiogram.types import Message
from httpx import AsyncClient
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
    try:
        response = await session.get(
            timeout=1,
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


async def weather(message: Message):
    city = message.get_args()
    if city == '':
        city = 'Тюмень'
    session = httpx.AsyncClient()
    cnt = 4
    api_response = await get_weather(session, city, 'forecast', cnt)
    if not api_response:
        await message.reply('Конекшон тимеаут')
        await session.aclose()
        return
    cod = int(api_response['cod'])
    if cod // 100 != 2:
        if cod == 404:
            await message.reply('Такого города не существует')
        else:
            await message.reply('Пошел нахуй')
        await session.aclose()
        return

    text = f"Погода для города <b>{api_response['city']['name']}</b>\n\n"
    for time_range in range(api_response['cnt']):
        api_data = api_response['list'][time_range]
        api_weather = api_data['weather'][0]
        if time_range == 0:
            text += '<i><b>Сейчас</b></i>'
        else:
            text += f"<i><b>В {calculate_time(time_range, api_response)}</b></i>"
        text += f"\n🌡 <b>{round(api_data['main']['temp'])}°</b>\n"\
                f"{icon_id[api_weather['id']]} {str(api_weather['description']).capitalize()}\n"\
                f"💨 <b>{round(api_data['wind']['speed'])} м/с</b>\n\n"

    await message.reply(text)
    await session.aclose()


def register(dp):
    dp.register_message_handler(weather, commands=['w', 'weather'])
