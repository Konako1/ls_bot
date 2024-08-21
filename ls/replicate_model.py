import replicate
from aiogram import Dispatcher
from aiogram.types import Message

from secret_chat import config


async def generate_image(message: Message):
    prompt = message.get_args()
    if prompt == '':
        await message.reply('Напиши промпт на английском')
    client = replicate.Client(api_token=config.REPLICATE_TOKEN)
    try:
        output = await client.async_run(
            "bytedance/sdxl-lightning-4step:727e49a643e999d602a896c774a0658ffefea21465756a6ce24b7ea4165eba6a",
            input={
                "prompt": prompt,
                "num_outputs": 1,
                "scheduler": "K_EULER",
            }
        )
    except Exception as e:
        await message.reply(str(e))
        return

    await message.reply_photo(output[0])


def setup(dp: Dispatcher):
    dp.register_message_handler(generate_image, commands=['generate'])
