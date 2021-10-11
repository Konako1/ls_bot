import os
import subprocess
import pywinauto
from pprint import pprint

server = 'Minecraft* 1.16.5 - Multiplayer (LAN)'


async def is_server_open():
    # tasklist = subprocess.Popen('tasklist')
    # print(tasklist)
    windows = pywinauto.Desktop(backend='uia').windows()
    window_names = [w.window_text() for w in windows]
    return True if server in window_names else False
