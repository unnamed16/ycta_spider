__licence__ = 'MIT'
__author__ = 'pvp'
__credits__ = ['pvp']
__maintainer__ = 'pvp'
__date__ = '2022/05/30'

import datetime as dt
from dataclasses import dataclass
from typing import List

from ycta_spider.structures.common import SourceInfo


@dataclass
class VideoInfo(SourceInfo):
    publish_time: dt.datetime
    title: str
    description: str
    channel_id: str
    duration: str = None
    channel_title: str = None
    tags: List[str] = None
    category_id: int = None
    view_count: int = None
    like_count: int = None
    comment_count: int = None
    topic_categories: List[str] = None


@dataclass
class ChannelInfo(SourceInfo):
    pass
    # TODO


@dataclass
class PrimaryComment(SourceInfo):
    pass
    # TODO


@dataclass
class SecondaryComment(SourceInfo):
    pass
    # TODO



@dataclass
class Channel:
    channel_id: str
    name: str = None
    is_anti_put: int = None
    suffix: str = None
    desc: str = None


Channels = List[Channel]
