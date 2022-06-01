__licence__ = 'MIT'
__author__ = 'pvp'
__credits__ = ['pvp']
__maintainer__ = 'pvp'
__date__ = '2022/05/30'

import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import List


class SearchOrder(Enum):
    DATE = 'date'
    RATING = 'rating'
    RELEVANCE = 'relevance'
    TITLE = 'title'
    VIDEO_COUNT = 'videoCount'
    VIEW_COUNT = 'viewCount'


@dataclass
class VideoData:
    videoId: str
    publishedAt: dt.datetime
    title: str
    description: str


@dataclass
class Channel:
    name: str = None
    is_antiput: int = None
    suffix: str = None
    desc: str = None
    channelId: str = None


Channels = List[Channel]
