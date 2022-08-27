from __future__ import annotations

__licence__ = 'MIT'
__author__ = 'pvp'
__credits__ = ['pvp']
__maintainer__ = 'pvp'
__date__ = '2022/05/30'

import datetime as dt
from dataclasses import field
from enum import Enum
from typing import List, Tuple, Union, Iterable
from dateutil.parser import isoparse

from ycta_spider.structures.common import Source, Comment, dklass_kwonly


@dklass_kwonly
class YoutubeVideo(Source):
    publish_time: dt.datetime = None
    title: str = None
    description: str = None
    channel_id: str = None
    duration: str = None
    channel_title: str = None
    tags: List[str] = None
    category_id: int = None
    view_count: int = None
    like_count: int = None
    comment_count: int = None
    topic_categories: List[str] = None

@dklass_kwonly
class YoutubeComment(Comment):
    text_original: str
    etag: str
    author_display_name: str
    author_channel_id: str
    like_count: int
    published_at: dt.datetime
    updated_at: dt.datetime

def _comment_to_relevant_dict(comment: dict) -> dict:
    snippet = comment['snippet']
    return {
        'idx': comment['id'],
        'etag': comment['etag'],
        'text': snippet['textDisplay'],
        'text_original': snippet['textOriginal'],
        'author_display_name': snippet['authorDisplayName'],
        'author_channel_id': snippet['authorChannelId']['value'],
        'like_count': snippet['likeCount'],
        'published_at': isoparse(snippet['publishedAt']),
        'updated_at': isoparse(snippet['updatedAt'])
    }


@dklass_kwonly
class YoutubePrimaryComment(YoutubeComment):
    video_id: str
    total_reply_count: int = 0
    children_idx_suff: List[str] = field(default_factory=lambda: [])

    @property
    def children_idx(self):
        return ['.'.join([self.idx, suff]) for suff in self.children_idx_suff]

YoutubePrimaryComment.build()

@dklass_kwonly
class YoutubeSecondaryComment(YoutubeComment):
    @property
    def parent_idx(self) -> str:
        return self.idx.split('.')[0]


YoutubeSecondaryComment.build()


def process_top_level_comments(comment: dict) -> Tuple[YoutubePrimaryComment, List[YoutubeSecondaryComment]]:
    replies = comment.get('replies', {'comments': []})['comments']
    secondary_comments = [YoutubeSecondaryComment(**_comment_to_relevant_dict(reply)) for reply in replies]
    snippet = comment['snippet']
    primary_comment = YoutubePrimaryComment(
        video_id=snippet['videoId'],
        total_reply_count=snippet['totalReplyCount'],
        children_idx_suff=[c.idx.split('.')[1] for c in secondary_comments],
        **_comment_to_relevant_dict(snippet['topLevelComment']))
    return primary_comment, secondary_comments


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


YoutubeInfo = Iterable[Union[YoutubeVideo, YoutubeChannel, YoutubePrimaryComment, YoutubeSecondaryComment]]