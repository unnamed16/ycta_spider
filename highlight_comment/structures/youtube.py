__licence__ = 'MIT'
__author__ = 'pvp'
__credits__ = ['pvp']
__maintainer__ = 'pvp'
__date__ = '2022/05/30'

import datetime as dt
from dataclasses import dataclass
from typing import List


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


@dataclass
class VideoInfo:
    id: str
    time: dt.datetime
    channelId: str
    title: str
    description: str
    channelTitle: str
    tags: List[str]
    categoryId: int
    duration: str
    viewCount: int
    likeCount: int
    commentCount: int
    topicCategories: List[int]


VideoInfos = List[VideoInfo]
