import random
from dataclasses import dataclass

from secret_chat.config import ls_group_id

symbols = [
    '+',
    '-',
    '*',
    '/',
    '^'
]


@dataclass()
class NumInfo:
    number: float
    digit: int


def math(username: str, chat_id: int) -> tuple[str, float, bool]:
    is_funny_number = False
    r_symbol = random.choice(symbols)
    first_num = random_num()
    second_num = random_num()
    final_math = do_math(first_num, second_num, r_symbol)

    if abs(final_math) in (228, 322, 727, 420, 1337, 1488):
        is_funny_number = True

    text = final_math
    if len(str(final_math)) > 100:
        num_len = len(str(final_math))
        text = f'{str(final_math)[:100]}\nи это только первые 100 знаков, так что иди как ты нахуй\n' \
               f'({num_len} цыфор в оригинале)'

    if str(second_num).startswith('-'):
        second_num = f'({second_num})'

    simple_math = f'Я посчитал какую-то ненужную хуйню за тебя, {username}:\n' \
                  f'{first_num} {r_symbol} {second_num} = {text}'

    if is_funny_number and chat_id == ls_group_id:
        simple_math += '\n<b>ATTENTION</b> <code>Funny number alert</code> <b>ATTENTION</b>' \
                       '\n@konako1 @MusyaTheGreat @evgfilim1 @ElonMusk @RealDonaldTrump @Cookiezi'

    return simple_math, final_math, is_funny_number


def do_math(first_num: int, second_num: int, symbol: str) -> float:
    if symbol == '+':
        return first_num + second_num
    if symbol == '-':
        return first_num - second_num
    if symbol == '*':
        return first_num * second_num
    if symbol == '/':
        return first_num / second_num
    return first_num ** second_num


def random_num() -> int:
    return random.randint(-100000, 100000)
