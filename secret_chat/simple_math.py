import random
import json
import time
from dataclasses import dataclass

from secret_chat.config import json_path, ls_group_id

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


class Calls:
    def __init__(self):
        self._calls_storage = {}
        self.calls_load()

    def calls_load(self):
        try:
            with open(json_path + 'calls_chest.json', encoding='utf8') as f:
                self._calls_storage = json.load(f)
        except FileExistsError:
            pass

    def save_calls(self):
        with open(json_path + 'calls_chest.json', 'w', encoding='utf8') as f:
            json.dump(self._calls_storage, f, ensure_ascii=False, )

    def get_say_count(self) -> int:
        return self._calls_storage['says_count']

    def get_deaths_count(self) -> int:
        return self._calls_storage['deaths_count']

    def get_nice_pfp_calls(self) -> int:
        return self._calls_storage['nice_pfp']

    def get_lowest_num(self) -> NumInfo:
        return NumInfo(
            number=self._calls_storage['lowest_num']['num'],
            digit=self._calls_storage['lowest_num']['digit'],
        )

    def get_highest_num(self) -> NumInfo:
        return NumInfo(
            number=self._calls_storage['highest_num']['num'],
            digit=self._calls_storage['highest_num']['digit'],
        )

    def get_number_one_name(self) -> str:
        return self._calls_storage['number_one_name']

    def get_number_one_time(self) -> float:
        return self._calls_storage['number_one_time']

    def say_was_sayed(self):
        self._calls_storage['says_count'] += 1
        self.save_calls()

    def golub_was_found(self):
        self._calls_storage['deaths_count'] += 1
        self.save_calls()

    def nice_pfp_sayed(self):
        self._calls_storage['nice_pfp'] += 1
        self.save_calls()

    def update_lowest_num(self, num: float, digit: int):
        self._calls_storage['lowest_num']['num'] = num
        self._calls_storage['lowest_num']['digit'] = digit
        self.save_calls()

    def update_highest_num(self, num: float, digit: int):
        self._calls_storage['highest_num']['num'] = num
        self._calls_storage['highest_num']['digit'] = digit
        self.save_calls()

    def update_number_one_name(self, name: str):
        self._calls_storage['number_one_name'] = name
        self.save_calls()

    def update_number_one_time(self, time: float):
        self._calls_storage['number_one_time'] = time
        self.save_calls()


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
