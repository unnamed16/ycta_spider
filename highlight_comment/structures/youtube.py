__licence__ = 'MIT'
__author__ = 'pvp'
__credits__ = ['pvp']
__maintainer__ = 'pvp'
__date__ = '2022/05/30'

from dataclasses import dataclass
from typing import List

from highlight_comment.structures.common import SourceInfo


@dataclass
class VideoInfo(SourceInfo):
    title: str
    description: str
    duration: str = None
    channel_id: str = None
    channel_title: str = None
    tags: List[str] = None
    category_id: int = None
    view_count: int = None
    like_count: int = None
    comment_count: int = None
    topic_categories: List[int] = None


@dataclass
class Channel:
    name: str = None
    is_anti_put: int = None
    suffix: str = None
    desc: str = None
    channel_id: str = None


Channels = List[Channel]
