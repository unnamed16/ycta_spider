import datetime as dt
import os
from csv import reader, writer
from dataclasses import dataclass
from enum import Enum
from typing import List

from highlight_comment.file_manager.reader import read_config


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


ID_SUFFIXES = ['c', 'channel', 'user']


@dataclass
class Channel:
    name: str
    is_antiput: int
    suffix: str
    desc: str
    channelId: str = None


Channels = List[Channel]


class ChannelCache:
    @staticmethod
    def cache_path():
        return os.path.join(read_config()['data_path'], 'youtube')

    @classmethod
    def load_channels(cls) -> Channels:
        channels = []
        with open(os.path.join(cls.cache_path(), 'channels.csv'), newline='') as csvfile:
            spamreader = reader(csvfile, delimiter=',', quotechar='|')
            next(spamreader)
            for (id, id_suff, is_antiput, desc) in spamreader:
                suff = ID_SUFFIXES[int(id_suff)]
                ch_kwargs = {'name': id, 'is_antiput': int(is_antiput), 'suffix': suff, 'desc': desc}
                if suff == 'channel':
                    ch_kwargs['channelId'] = id
                channels.append(Channel(**ch_kwargs))
        return channels

    @classmethod
    def add_channels(cls, name: str, is_antiput: int, suffix: str, desc: str):
        with open(os.path.join(cls.cache_path(), 'channels.csv'), 'a', newline='') as f:
            writer(f).writerow([name, ID_SUFFIXES.index(suffix), is_antiput, desc])
