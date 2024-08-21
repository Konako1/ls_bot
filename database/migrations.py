from pathlib import Path

import aiosqlite
from aiosqlite import Connection


async def migrate(connection_path: Path):
    connection = await aiosqlite.connect(connection_path)
    await connection.execute('CREATE TABLE IF NOT EXISTS calls(sign TEXT PRIMARY KEY NOT NULL,'
                             'num TEXT NOT NULL)')
    await connection.execute('CREATE TABLE IF NOT EXISTS frames(id INTEGER PRIMARY KEY AUTOINCREMENT, '
                             'frame INTEGER NOT NULL,'
                             'count INTEGER NOT NULL, '
                             'datetime FLOAT NOT NULL)')
    await connection.execute('CREATE TABLE IF NOT EXISTS stickers(sticker TEXT PRIMARY KEY NOT NULL,'
                             'datetime FLOAT NOT NULL,'
                             'probability INTEGER NOT NULL,'
                             'count INTEGER NOT NULL)')
    await connection.execute('CREATE TABLE IF NOT EXISTS stat(stat INTEGER PRIMARY KEY NOT NULL,'
                             'count INTEGER NOT NULL)')
    await connection.execute('CREATE TABLE IF NOT EXISTS pastes(paste TEXT PRIMARY KEY NOT NULL)')
    await connection.execute('CREATE TABLE IF NOT EXISTS aneks(anek_id INTEGER NOT NULL,'
                             'user_id INTEGER NOT NULL,'
                             'is_like INTEGER NOT NULL DEFAULT 1,'
                             'CHECK (is_like IN (1, 0)),'
                             'PRIMARY KEY (anek_id, user_id))')
    await connection.execute('CREATE TABLE IF NOT EXISTS silences(user_id INTEGER PRIMARY KEY NOT NULL,'
                             'is_silenced INTEGER NOT NULL,'
                             'CHECK (is_silenced IN (1, 0)))')
    await connection.execute('CREATE TABLE IF NOT EXISTS aneks_saves(message_id INTEGER NOT NULL,'
                             'chat_id INTEGER NOT NULL,'
                             'is_saved INTEGER NOT NULL,'
                             'CHECK (is_saved in (1, 0)),'
                             'PRIMARY KEY(message_id, chat_id))')
    await connection.execute('CREATE TABLE IF NOT EXISTS ping_commands('
                             'id INTEGER PRIMARY KEY NOT NULL, chat_id INTEGER NOT NULL,'
                             'command TEXT NOT NULL)')
    await connection.execute('CREATE TABLE IF NOT EXISTS ping_users(user_id INTEGER PRIMARY KEY NOT NULL,'
                             'username TEXT NOT NULL)')
    await connection.execute('CREATE TABLE IF NOT EXISTS command_user('
                             'command_id INTEGER NOT NULL REFERENCES ping_commands(id),'
                             'user_id INTEGER NOT NULL REFERENCES ping_users(user_id),'
                             'UNIQUE(command_id, user_id))')
    await connection.execute('CREATE TABLE IF NOT EXISTS modeus('
                             'user_id INTEGER PRIMARY KEY NOT NULL,'
                             'modeus_id TEXT NOT NULL,'
                             'fc_toggle INTEGER NOT NULL DEFAULT 1)')
    await connection.execute('CREATE TABLE IF NOT EXISTS wysi('
                             'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                             'regnum TEXT NOT NULL,'
                             'region INTEGER,'
                             'date_created DATE)')
    await connection.execute('CREATE TABLE IF NOT EXISTS locations('
                             'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                             'city TEXT NOT NULL,'
                             'user_id INTEGER,'
                             'UNIQUE(city, user_id))')
    await connection.execute('CREATE TABLE IF NOT EXISTS mashup_posts('
                             'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                             'post_link TEXT NOT NULL, '
                             'song_name TEXT NOT NULL, '
                             'like_count INTEGER NOT NULL, '
                             'view_count INTEGER NOT NULL, '
                             'UNIQUE(post_link))')
    await connection.commit()
