from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass()
class StickerInfo:
    name: str
    date: datetime
    probability: int
    count: int


@dataclass()
class Statistic:
    say_count: int
    pigeon_count: int
    nice_pfp_count: int
    anek_count: int


@dataclass()
class StatType:
    say = 1
    pigeon = 2
    nice_pfp = 3
    anek = 4


@dataclass()
class Frame:
    frame: int
    datetime: float
    count: int


@dataclass()
class SilenceInfo:
    is_silenced: Optional[bool]
    title: Optional[str]


@dataclass()
class Mashup:
    post_link: str
    song_name: str
    like_count: int
    view_count: str