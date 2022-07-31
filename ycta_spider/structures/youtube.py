from __future__ import annotations

__licence__ = 'MIT'
__author__ = 'pvp'
__credits__ = ['pvp']
__maintainer__ = 'pvp'
__date__ = '2022/05/30'

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import List

from ycta_spider.structures.common import Source, Comment


class YoutubeVideo(Source):
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

class YoutubeComment(Comment):
    parent_idx: str = ''
    children_idx: List = field(default_factory=lambda: [])

    @property
    def has_children(self) -> bool:
        return len(self.children_idx) > 0

class YoutubeChannel(Source):
    channel_id: str
    name: str = None
    is_anti_put: int = None
    suffix: str = None
    desc: str = None

class SearchOrder(Enum):
    DATE = 'date'
    TIME = 'time'
    RATING = 'rating'
    RELEVANCE = 'relevance'
    TITLE = 'title'
    VIDEO_COUNT = 'videoCount'
    VIEW_COUNT = 'viewCount'
