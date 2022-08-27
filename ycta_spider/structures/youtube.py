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
from isodate import parse_duration

from ycta_spider.structures.common import Source, Comment, dklass_kwonly

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

    @classmethod
    def inst_from_psql_output(cls, vals: List) -> YoutubePrimaryComment:
        inst = super().inst_from_psql_output(vals)
        if inst.total_reply_count == 0:
            inst.children_idx_suff = []
        return inst  # noqa

YoutubePrimaryComment.build()

@dklass_kwonly
class YoutubeSecondaryComment(YoutubeComment):
    @property
    def parent_idx(self) -> str:
        return self.idx.split('.')[0]


YoutubeSecondaryComment.build()
YoutubeCommentBundle = Tuple[YoutubePrimaryComment, List[YoutubeSecondaryComment]]


def process_top_level_comments(comment: dict) -> YoutubeCommentBundle:
    replies = comment.get('replies', {'comments': []})['comments']
    secondary_comments = [YoutubeSecondaryComment(**_comment_to_relevant_dict(reply)) for reply in replies]
    snippet = comment['snippet']
    primary_comment = YoutubePrimaryComment(
        video_id=snippet['videoId'],
        total_reply_count=snippet['totalReplyCount'],
        children_idx_suff=[c.idx.split('.')[1] for c in secondary_comments],
        **_comment_to_relevant_dict(snippet['topLevelComment']))
    return primary_comment, secondary_comments


@dklass_kwonly
class YoutubeVideo(Source):
    etag: str
    published_at: dt.datetime
    channel_id: str
    title: str
    description: str
    duration: float  # in seconds
    category_id: int
    view_count: int
    like_count: int
    comment_count: int
    tags: List[str]
    topic_categories: List[str]

    @classmethod
    def from_get_response(cls, response: dict) -> YoutubeVideo:
        assert len(response['items']) == 1
        item = response['items'][0]
        snippet = item['snippet']
        stats = item['statistics']
        kwargs = dict(
            idx=item['id'],
            etag=item['etag'],
            published_at=snippet['publishedAt'],
            channel_id=snippet['channelId'],
            title=snippet['title'],
            description=snippet['description'],
            duration=parse_duration(item['contentDetails']['duration']).total_seconds(),
            view_count=stats['viewCount'],
            like_count=stats['likeCount'],
            comment_count=stats['commentCount'],
            category_id=snippet['categoryId'],
            tags=snippet['tags'],
            topic_categories=item['topicDetails']['topicCategories'],
        )
        return cls(**kwargs)  # noqa

YoutubeVideo.build()


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