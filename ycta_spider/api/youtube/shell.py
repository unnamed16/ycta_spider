__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/28'

from typing import Callable, Dict, List, Iterator
import json
from dateutil.parser import isoparse
from datetime import datetime
from datetime import timedelta
import time

import requests

from ycta_spider.structures.youtube import Channel, VideoInfo
from ycta_spider.api.shell import Shell as CommonShell
from ycta_spider.api.shell import PlatformType, ResponseCode, SearchOrder
from ycta_spider.api.shell import Source, Response, Comment, Comments


class Shell(CommonShell):
    __CHID_OFFSET_FROM = 13
    __CHID_OFFSET_TO = 37
    __V3_URL = 'https://www.googleapis.com/youtube/v3/'
    __OAUTH2_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    __SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
    __REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
    __TOKEN_URL = "https://www.googleapis.com/oauth2/v4/token"
    __DEFAULT_INFO_LIMIT = 50
    __INFO_BATCH_SIZE = 50
    __COMMENTS_BATCH_SIZE = 100

    def __init__(self):
        super().__init__()
        self.__platform_type = PlatformType.YOUTUBE
        platform_config = self.config['platforms'][self.platform_type.name]
        self.__sources = self.update_sources()
        self.__api_key = platform_config['api_key']
        self.__client_id = platform_config['client_id']
        self.__client_secret = platform_config['client_secret']
        self.__access_token = platform_config['access_token']

    def get_authorization_link(self) -> str:
        return str(
            f"{self.__OAUTH2_URL}?"
            f"client_id={self.__client_id}&"
            f"response_type=code&"
            f"scope={self.__SCOPE}&"
            f"access_type=offline&redirect_uri={self.__REDIRECT_URI}"
        )

    def get_access_token(self, authorization_code: str) -> Dict[str, str]:
        access_token = requests.post(self.__TOKEN_URL, data={
            "client_id": self.__client_id,
            "client_secret": self.__client_secret,
            "code": authorization_code,
            "redirect_uri": self.__REDIRECT_URI,
            "grant_type": "authorization_code"
        })
        return json.loads(access_token.text)

    def get_comments(
            self,
            source: Source,
            limit: int = None,
            order: SearchOrder = SearchOrder.RELEVANCE,
            page_token: str = '') -> Iterator[Comment]:
        """
        Return all comments for the specified source\n
        :param source: ('videoId', 'MyVideoId')
        :param limit: will download all the comments if None
        :param order: time (starts with more recent) or relevance
        :param page_token: is needed for recursive upload from a concrete page
        :return: generator of comments
        """
        func = 'commentThreads'
        part = 'snippet,replies,id'
        query = str(
            f'{self.__V3_URL}{func}?'
            f'part={part}&'
            f'{source[0]}={source[1]}&'
            f'key={self.__api_key}&'
            f'maxResults={self.__COMMENTS_BATCH_SIZE if limit is None else min(self.__COMMENTS_BATCH_SIZE, limit)}&'
            f'order={order.value}'
        )
        response = requests.get(f'{query}&pageToken={page_token}', headers=self.common_headers)
        comments = Shell.__parse(response, Shell.__parse_comments)
        if comments['code'] == ResponseCode.OK:
            for comment in comments['result']:
                yield comment
            next_page_token = response.json().get('nextPageToken', None)
            if next_page_token is not None:
                for comment in self.get_comments(
                        source,
                        limit=None if limit is None else limit - self.__COMMENTS_BATCH_SIZE,
                        order=order,
                        page_token=next_page_token):
                    yield comment

    @staticmethod
    def __parse_comments(comments_json: Dict) -> Comments:
        for comment in comments_json['items']:
            yield Shell.__parse_parent_comment(comment)

    def get_comments_from_several_sources(
            self,
            sources: List[Source] = None,
            limit: int = None,
            order: SearchOrder = SearchOrder.RELEVANCE) -> Iterator[Comment]:
        """
        Return all comments for the several specified sources\n
        :param sources: source descriptions list where from the comments have to be obtained
        :param limit: limit of the comments to download from each source
        :param order: sort order of the obtained data
        :return: Generator of the Comments
        """
        if sources is None:
            sources = self.__sources
        for i, source in enumerate(sources):
            print(f'\r{i+1}/{len(sources)}\tDownloading comments from {source}', end='')
            for comment in self.get_comments(source, limit, order=order):
                yield comment
        print('\r ', end='')
        print('\r', end='')

    def get_comments_from_several_sources_continuous(
            self,
            sources: List[Source] = None,
            limit: int = None,
            order: SearchOrder = SearchOrder.RELEVANCE) -> Iterator[Comment]:
        """
        Return all comments for the several specified sources and update it continuously\n
        :param sources: source descriptions list where from the comments have to be obtained
        :param limit: limit of the comments to download from each source
        :param order: sort order of the obtained data
        :return: Generator of the Comments
        """
        last_update_time_fresh = datetime.now() - timedelta(seconds=self.__COMMENTS_RARE_RANGE)
        last_update_time_medium = last_update_time_fresh
        last_update_time_rare = last_update_time_fresh
        local_sources_fresh = []
        local_sources_medium = []
        local_sources_rare = []
        while True:
            current_time = datetime.now()
            if current_time > last_update_time_fresh + timedelta(seconds=self.__COMMENTS_CONTINUOUS_DELAY_FRESH):
                local_sources_fresh = self.get_sources_info_from_db(
                    min_ts=current_time - timedelta(seconds=self.__COMMENTS_FRESH_RANGE),
                    max_ts=current_time
                ) if sources is None else sources
                last_update_time_fresh = current_time
            if current_time > last_update_time_medium + timedelta(seconds=self.__COMMENTS_CONTINUOUS_DELAY_MEDIUM):
                local_sources_medium = self.get_sources_info_from_db(
                    min_ts=current_time - timedelta(seconds=self.__COMMENTS_MEDIUM_RANGE),
                    max_ts=current_time - timedelta(seconds=self.__COMMENTS_FRESH_RANGE),
                ) if sources is None else []
                last_update_time_medium = current_time
            if current_time > last_update_time_rare + timedelta(seconds=self.__COMMENTS_CONTINUOUS_DELAY_RARE):
                local_sources_rare = self.get_sources_info_from_db(
                    min_ts=current_time - timedelta(seconds=self.__COMMENTS_RARE_RANGE),
                    max_ts=current_time - timedelta(seconds=self.__COMMENTS_MEDIUM_RANGE),
                ) if sources is None else []
                last_update_time_rare = current_time
            if local_sources_fresh:
                for s in self.get_comments_from_several_sources(sources=local_sources_fresh, limit=limit, order=order):
                    yield s
                local_sources_fresh = None
            if local_sources_medium:
                for s in self.get_comments_from_several_sources(sources=local_sources_medium, limit=limit, order=order):
                    yield s
                local_sources_medium = None
            if local_sources_rare:
                for s in self.get_comments_from_several_sources(sources=local_sources_rare, limit=limit, order=order):
                    yield s
                local_sources_rare = None
            time_delay = \
                last_update_time_fresh + timedelta(seconds=self.__COMMENTS_CONTINUOUS_DELAY_FRESH) - datetime.now()
            if time_delay > timedelta(seconds=0):
                time.sleep(time_delay.total_seconds())

    @staticmethod
    def __parse_parent_comment(thread: Dict) -> Comment:
        _thread_id = thread['id']
        _main_comment = thread['snippet']
        result = Shell.__parse_one_comment(
            _main_comment['topLevelComment'],
            _thread_id,
            is_top_level=True,
            reply_count=_main_comment['totalReplyCount'])
        if 'replies' in thread:
            result['replies'] = [
                Shell.__parse_one_comment(reply, _thread_id)
                for reply in thread['replies']['comments']
            ]
        return result

    def add_comment(self, source: Source, comment: str) -> Response:
        func = 'commentThreads'
        part = 'snippet'
        query = f'{self.__V3_URL}{func}?part={part}&{source}&key={self.__api_key}'
        headers = dict(self.common_headers)
        headers['Authorization'] = f'Bearer {self.__access_token}'
        data = {
            "snippet": {
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": comment
                    }
                },
                "videoId": source
            }
        }
        comments = requests.post(query, headers=headers, data=data)
        # TODO: make proper parser for the response
        return Shell.__parse(comments, Shell.__parse_one_comment)

    @staticmethod
    def __parse_one_comment(
            comment_json: Dict,
            thread_id: str,
            is_top_level: bool = False,
            reply_count: int = 0) -> Comment:
        _comment_id = comment_json['id']
        snippet = comment_json['snippet']
        _video_id = snippet['videoId']
        _all_ids = {
            'video_id': _video_id,
            'thread_id': thread_id,
            'comment_id': _comment_id
        }
        _text = snippet['textDisplay']
        _likes = snippet['likeCount']
        _published = snippet['publishedAt']
        _parent = None if is_top_level else snippet['parentId']
        _author_id = snippet.get('authorChannelId', {'value': ''})['value']
        _meta_info = {
            'is_top_level': is_top_level,
            'reply_count': reply_count,
            'publish_date': _published,
            'parent_comment_id': _parent,
            'author_id': _author_id,
            'author_name': snippet['authorDisplayName']
        }
        return {
            'ids': _all_ids,
            'text': _text,
            'meta': _meta_info,
            'likes': _likes
        }

    def get_source_info(
            self,
            source: Source,
            limit: int = __DEFAULT_INFO_LIMIT,
            order: SearchOrder = SearchOrder.DATE) -> Iterator[VideoInfo]:
        """
        Return info for the specified source or sub sources if the source is not a leaf\n
        :param source: ('videoId', 'MyVideoId'), ('videoIdList', [list of 'video ids'])
        or ('channelId', 'MyChannelId')
        :param limit: limit of the sub-sources to process
        :param order: sort order of the obtained data (date, rating, title), used only for channel source
        :return: Generator of the VideoInfo
        """
        source_type, source_value = source
        if source_type == 'videoId':
            response = self.__get_videos_info([source_value])
        elif source_type == 'videoIdList':
            videos_num = len(source_value)
            assert videos_num <= limit, f'the limit is {limit}, video id list has length {videos_num}'
            response = self.__get_videos_info(source_value)
        elif source_type == 'channelId':
            response = self.__get_video_ids(Channel(channel_id=source_value), limit=limit, order=order)
            if response['code'] == ResponseCode.OK:
                response = self.__get_videos_info([video_info.idx for video_info in response['result']])
        else:
            raise KeyError(f'unknown source type: {source_type}')
        if response['code'] == ResponseCode.OK:
            for source_info in response['result']:
                yield source_info

    def get_sources_info_continuous(
            self,
            sources: List[Source] = None,
            limit: int = __DEFAULT_INFO_LIMIT,
            order: SearchOrder = SearchOrder.DATE) -> Iterator[VideoInfo]:
        """
        Return info for the several specified sources and update it continuously\n
        :param sources: source descriptions list for which the info has to be obtained
        :param limit: limit of the sources obtained from each source
        :param order: sort order of the obtained data
        :return: Generator of the SourceInfo
        """
        # repeat every __INFO_CONTINUOUS_DELAY seconds
        prev_time = datetime.now()
        while True:
            local_sources = self.update_sources() if sources is None else sources
            for s in self.get_sources_info(sources=local_sources, limit=limit, order=order):
                yield s
            prev_time += timedelta(seconds=self.__INFO_CONTINUOUS_DELAY)
            time_delay = prev_time - datetime.now()
            if time_delay > timedelta(seconds=0):
                time.sleep(time_delay.total_seconds())

    def get_sources_info_from_db(self, min_ts, max_ts) -> Iterator[Source]:
        return self.config['sources'][self.platform_type.name]
        # TODO: get sources from Info DB

    def update_sources(self) -> Iterator[Source]:
        return self.config['sources'][self.platform_type.name]
        # TODO: update sources from Sources DB

    def get_sources_info(
            self,
            sources: List[Source] = None,
            limit: int = __DEFAULT_INFO_LIMIT,
            order: SearchOrder = SearchOrder.DATE) -> Iterator[VideoInfo]:
        """
        Return info for the several specified sources\n
        :param sources: source descriptions list for which the info has to be obtained
        :param limit: limit of the sources obtained from each source
        :param order: sort order of the obtained data
        :return: Generator of the VideoInfo
        """
        if sources is None:
            sources = self.__sources
        for i, source in enumerate(sources):
            print(f'\r{i+1}/{len(sources)}\tDownloading info from {source}', end='')
            for source_info in self.get_source_info(source, limit=limit, order=order):
                yield source_info
        print('\r ', end='')
        print('\r', end='')

    def __get_video_ids(
            self,
            channel: Channel,
            limit: int = __DEFAULT_INFO_LIMIT,
            order: SearchOrder = SearchOrder.DATE,
            page_token: str = '') -> Response:
        part = 'snippet'
        content_type = 'video'
        func = 'search'
        if channel.channel_id is None:
            channel.channel_id = self.get_channel_id(channel.name, channel.suffix)['result']
        channel_id = channel.channel_id
        url = str(
            f'{self.__V3_URL}{func}?'
            f'part={part}&'
            f'channelId={channel_id}&'
            f'maxResults={min(limit, self.__INFO_BATCH_SIZE)}&'
            f'order={order.value}&'
            f'type={content_type}&'
            f'key={self.__api_key}&'
            f'pageToken={page_token}'
        )
        req = requests.get(url)
        result = Shell.__parse(req, Shell.__parse_video_ids)
        if result['code'] == ResponseCode.ERROR:
            result['message'] = f'failed to find videos on {channel_id}'
        elif result['code'] == ResponseCode.OK:
            rest_limit = limit - self.__INFO_BATCH_SIZE
            if rest_limit > 0:
                next_page_token = req.json().get('nextPageToken', None)
                if next_page_token is not None:
                    next_page = self.__get_video_ids(
                        channel,
                        limit=rest_limit,
                        order=order,
                        page_token=next_page_token
                    )
                    if next_page['code'] == ResponseCode.OK:
                        result['result'].extend(next_page['result'])
        return result

    @staticmethod
    def __parse_video_ids(response_json: Dict) -> List[VideoInfo]:
        return [
            VideoInfo(
                idx=json_elem['id']['videoId'],
                time=isoparse(json_elem['snippet']['publishedAt']),
                title=json_elem['snippet']['title'],
                description=json_elem['snippet']['description']
            )
            for json_elem in response_json['items']
        ]

    @classmethod
    def get_channel_id(cls, name: str, suffix: str) -> Response:
        url = f'https://www.youtube.com/{suffix}/{name}'
        req = requests.get(url, 'html.parser')
        if not req.ok:
            return {
                'code': ResponseCode.ERROR,
                'message': f'failed to fetch the source at {url}',
                'response.status_code': str(req.status_code),
                'response.reason': req.reason
            }
        text = req.text
        loc = text.find('externalId')
        if loc == -1:
            return {
                'code': ResponseCode.ERROR,
                'message': f'failed to find key identifier (externalId) on {suffix}/{name}'
            }
        return {
            'code': ResponseCode.OK,
            'result': text[loc + cls.__CHID_OFFSET_FROM: loc + cls.__CHID_OFFSET_TO]
        }

    @staticmethod
    def __parse(r: requests.Response, parser: Callable) -> Response:
        if not r.ok:
            return {
                'code': ResponseCode.ERROR,
                'response.status_code': str(r.status_code),
                'response.reason': r.reason
            }
        try:
            js = r.json()
            parsed = {
                'code': ResponseCode.OK,
                'result': parser(js)
            }
            return parsed
        except Exception as e:
            return {
                'code': ResponseCode.PARSE_ERROR,
                'message': str(e),
                'response.text': r.text
            }

    def __get_videos_info(self, videos: List[str]) -> Response:
        func = 'videos'
        part = ','.join([
            'statistics',
            'contentDetails',
            'id',
            'liveStreamingDetails',
            'localizations,player',
            'recordingDetails',
            'snippet',
            'status',
            'topicDetails'
        ])
        result = None
        for i in range(0, len(videos), self.__DEFAULT_INFO_LIMIT):
            ids = ','.join(videos[i:min(len(videos), i + self.__DEFAULT_INFO_LIMIT)])
            url = f'{self.__V3_URL}{func}?part={part}&id={ids}&key={self.__api_key}'
            req = requests.get(url, headers=self.common_headers)
            batch_result = self.__parse(req, self.__parse_video_info)
            if batch_result['code'] != ResponseCode.OK:
                return batch_result
            if result is None:
                result = batch_result
            else:
                result['result'].extend(batch_result['result'])
        return result

    @staticmethod
    def __parse_single_video_info(info: Dict) -> VideoInfo:
        snippet = info.get('snippet', dict())
        stats = info.get('statistics', dict())

        def __stats_int_or_none(key):
            return int(stats[key]) if key in stats else None

        return VideoInfo(
            idx=info.get('id', None),
            time=isoparse(snippet['publishedAt']) if 'publishedAt' in snippet else None,
            channel_id=snippet.get('channelId', None),
            title=snippet.get('title', None),
            description=snippet.get('description', None),
            channel_title=snippet.get('channelTitle', None),
            tags=snippet.get('tags', list()),
            category_id=int(snippet['categoryId']) if 'categoryId' in snippet else None,
            duration=info.get('contentDetails', dict()).get('duration', None),
            view_count=__stats_int_or_none('viewCount'),
            like_count=__stats_int_or_none('likeCount'),
            comment_count=__stats_int_or_none('commentCount'),
            topic_categories=info.get('topicDetails', dict()).get('topicCategories', None)
        )

    @staticmethod
    def __parse_video_info(request_json: Dict) -> List[VideoInfo]:
        return list(map(Shell.__parse_single_video_info, request_json['items']))
