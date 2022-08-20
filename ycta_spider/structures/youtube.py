from __future__ import annotations

__licence__ = 'MIT'
__author__ = 'pvp'
__credits__ = ['pvp']
__maintainer__ = 'pvp'
__date__ = '2022/05/30'

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple
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
    textOriginal: str
    etag: str
    authorDisplayName: str
    authorChannelId: str
    likeCount: int
    publishedAt: dt.datetime
    updatedAt: dt.datetime

def _comment_to_relevant_dict(comment: dict) -> dict:
    result = {'idx': comment['id'], 'etag': comment['etag']}
    snippet = comment['snippet']
    result['text'] = snippet['textDisplay']
    result.update({field: snippet[field] for field in ['textOriginal', 'authorDisplayName']})
    result['authorChannelId'] = snippet['authorChannelId']['value']
    result['likeCount'] = int(snippet['likeCount'])
    result.update({field: isoparse(snippet[field]) for field in ['publishedAt', 'updatedAt']})
    return result


@dklass_kwonly
class YoutubePrimaryComment(YoutubeComment):
    videoId: str
    totalReplyCount: int = 0
    children_idx: List[str] = field(default_factory=lambda: [])

YoutubePrimaryComment.build()

@dklass_kwonly
class YoutubeSecondaryComment(YoutubeComment):
    parent_idx: str

YoutubeSecondaryComment.build()

def process_top_level_comments(comment: dict) -> Tuple[YoutubePrimaryComment, List[YoutubeSecondaryComment]]:
    replies = comment['replies']['comments']
    snippet = comment['snippet']
    top_level_id = snippet['topLevelComment']['id']
    secondary_comments = []
    for reply in replies:
        secondary_comments.append(YoutubeSecondaryComment(parent_idx=top_level_id, **_comment_to_relevant_dict(reply)))
    primary_comment = YoutubePrimaryComment(
        videoId=snippet['videoId'],
        totalReplyCount=snippet['totalReplyCount'],
        children_idx=[c.idx for c in secondary_comments],
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
