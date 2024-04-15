import os
import subprocess
from io import BytesIO
from pathlib import Path

import httpx
from PIL import Image, WebPImagePlugin, ImageSequence
from aiogram import Dispatcher
from aiogram.types import Message, InputFile


def gen_frame(im: Image) -> Image:
    alpha = im.getchannel('A')
    im = im.convert('RGBA').convert('P', palette=Image.ADAPTIVE, colors=255)
    mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
    im.paste(255, mask)
    im.info['transparency'] = 255
    return im


def transform_webp(webp_bytes: BytesIO, name: str) -> Path:
    directory = Path.cwd().joinpath('7tv')
    gif = directory.joinpath(name + '.gif')
    webm = directory.joinpath(name + '.webm')
    png = directory.joinpath(name + '.png')

    im = Image.open(webp_bytes)

    if im.n_frames > 1:
        im_list = []
        for frame in ImageSequence.Iterator(im):
            frame = frame.convert('RGBA').resize((512, 512), Image.LANCZOS)
            frame = gen_frame(frame)
            im_list.append(frame)
        img = im_list[0]
        imgs = im_list[1:]
        img.save(gif, save_all=True, append_images=imgs, duration=50, loop=0, optimize=False, disposal=2)

        os.system(f'ffmpeg -i {gif.absolute()} -c:v libvpx-vp9 -filter:v scale=512:-1 -t 00:00:03 -c:a libopus {webm}')
        return gif

    im.save(png, save_all=True)
    return png


async def seven_tv(message: Message):
    url = message.get_args()
    client = httpx.AsyncClient()
    emote = await client.get(url)

    path = transform_webp(BytesIO(emote.content), 'test')
    await message.reply_animation(InputFile(path))
    #return await message.reply_sticker(InputFile(path))


def setup(dp: Dispatcher):
    dp.register_message_handler(seven_tv, commands=['stv'])
