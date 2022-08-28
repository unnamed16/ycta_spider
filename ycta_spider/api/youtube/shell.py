__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/28'

from typing import Callable, Dict, List, Iterator, Tuple, Union
import json
from dateutil.parser import isoparse
from datetime import datetime, timedelta
import time
from functools import partial

import pytz
import requests

from ycta_spider.structures.youtube import YoutubeChannel, YoutubeVideo, YoutubeComment, SearchOrder,\
    process_top_level_comments, YoutubePrimaryComment, YoutubeSecondaryComment, YoutubeCommentBundle,\
    YoutubeSourceDescription, YoutubeComments
from ycta_spider.api.shell import Shell
from ycta_spider.structures.common import PlatformType, ResponseCode, Source, Response
from ycta_spider.file_manager.writer import save_config
from ycta_spider.file_manager.reader import read_config


class YoutubeShell(Shell):
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
        self._platform_type = PlatformType.YOUTUBE
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

    def get_and_write_access_token(self, authorization_code: str):
        """writes access token to the config"""
        token = self.get_access_token(authorization_code)['access_token']
        config = read_config()
        for conf in (self.config, config):
            conf['platforms'][self.platform_type.name]['access_token'] = token
        save_config(config)

    def __query_builder(self, func: str, pars: dict=None) -> str:
        result = f'{self.__V3_URL}{func}'
        if pars is None or len(pars) == 0:
            return result
        return '?'.join([result, '&'.join([f'{k}={v}' for k, v in pars.items()] + ['key=' + self.__api_key])])


    def get_comments(
            self,
            source: str,
            limit: int = None,
            order: SearchOrder = SearchOrder.RELEVANCE,
            page_token: str = '') -> Iterator[YoutubeCommentBundle]:
        """
        Return all comments for the specified source\n
        :param source: videoId (11 letters)
        :param limit: will download all the comments if None
        :param order: time (starts with more recent) or relevance
        :param page_token: is needed for recursive upload from a concrete page
        :return: generator of pairs (primary comment, secondary comments)
        """
        max_results = self.__COMMENTS_BATCH_SIZE if limit is None else min(self.__COMMENTS_BATCH_SIZE, limit)
        query = self.__query_builder(func='commentThreads', pars={
            'part': 'snippet,replies,id',
            'videoId': source,
            'maxResults': max_results,
            'order': order.value,
            'pageToken': page_token
        })
        response = requests.get(query, headers=self.common_headers)
        comments = YoutubeShell.__parse(response, YoutubeShell.__parse_comments)
        if comments.code == ResponseCode.OK:
            for comment in comments.content['result']:
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
    def __parse_comments(comments_json: Dict) -> YoutubeComments:
        for comment in comments_json['items']:
            yield YoutubeShell.__parse_top_level_comment(comment)

    def get_comments_from_several_sources(
            self,
            sources: List[str] = None,
            limit: int = None,
            order: SearchOrder = SearchOrder.RELEVANCE) -> YoutubeComments:
        """
        Return all comments for the several specified sources\n
        :param sources: video ids
        :param limit: limit of the comments to download from each source
        :param order: sort order of the obtained data
        :return: Generator of the Comments
        """
        if sources is None:
            sources = self.__sources
        for i, source in enumerate(sources):
            print(f'\r{i + 1}/{len(sources)}\tDownloading comments from {source}', end='')
            for comment in self.get_comments(source, limit, order=order):  # noqa
                yield comment
        print('\r ', end='')
        print('\r', end='')

    def get_comments_from_several_sources_continuous(
            self,
            sources: List[str] = None,
            limit: int = None,
            order: SearchOrder = SearchOrder.RELEVANCE) -> YoutubeComments:
        """
        Return all comments for the several specified sources and update it continuously\n
        :param sources: list of video ids
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
            # TODO: a lot of copy-paste here
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
    def __parse_top_level_comment(comment: Dict) -> YoutubeCommentBundle:
        return process_top_level_comments(comment)

    def add_comment(self, source: str, comment: str) -> Response:
        """
        :param source: videoId
        :param comment: text of the message
        :return: response
        """
        query = self.__query_builder(func='commentThreads', pars={'part': 'snippet', 'videoId': source})
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
        return Response(code=ResponseCode.ERROR, content={'message': 'add comment parser not implemented'})

    def get_channels_info(self, ids: List[str]) -> Response:
        part = ','.join([
            'brandingSettings',
            'contentDetails',
            'contentOwnerDetails',
            'id',
            'localizations',
            'snippet',
            'statistics',
            'status',
            'topicDetails'
        ])
        url = self.__query_builder(func='channels', pars={'part': part, 'id': ','.join(ids)})
        req = requests.get(url)
        return self.__parse(req, YoutubeChannel.from_get_response_multiple)

    def get_source_info(
            self,
            source: YoutubeSourceDescription,
            limit: int = __DEFAULT_INFO_LIMIT,
            order: SearchOrder = SearchOrder.DATE) -> Response:
        """
        Return video info for a specified source

        :param source: ('videoId', 'video id'), ('videoIdList', [list of video ids]) or ('channelId', 'channel id')
        :param limit: limit of the sub-sources to process
        :param order: sort order of the obtained data (date, rating, title), used only for channel source
        :return:
        """
        source_type, source_value = source
        if source_type == 'videoId':
            return self._get_videos_info([source_value])
        elif source_type == 'videoIdList':
            videos_num = len(source_value)
            assert videos_num <= limit, f'the limit is {limit}, video id list has length {videos_num}'
            return self._get_videos_info(source_value)
        elif source_type == 'channelId':
            response = self._get_video_ids(channel_id=source_value, limit=limit, order=order)
            if response.code == ResponseCode.OK:
                return self._get_videos_info(response.content['result'])
            else:
                return response
        else:
            raise KeyError('unknown source type: ' + source_type)

    def get_sources_info_continuous(
            self,
            sources: List[YoutubeSourceDescription] = None,
            limit: int = __DEFAULT_INFO_LIMIT,
            order: SearchOrder = SearchOrder.DATE) -> Iterator[YoutubeVideo]:
        """
        Return info for the several specified sources and update it continuously\n
        :param sources: source descriptions list for which the info has to be obtained
        :param limit: limit of the sources obtained from each source
        :param order: sort order of the obtained data
        :return: Generator of the Source
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

    def update_sources(self) -> Iterator[Tuple[str, str]]:
        return self.config['sources'][self.platform_type.name]
        # TODO: update sources from Sources DB

    def get_sources_info(
            self,
            sources: List[YoutubeSourceDescription] = None,
            limit: int = __DEFAULT_INFO_LIMIT,
            order: SearchOrder = SearchOrder.DATE) -> Iterator[YoutubeVideo]:
        """
        Return info for the several specified sources\n
        :param sources: source descriptions list for which the info has to be obtained
        :param limit: limit of the sources obtained from each source
        :param order: sort order of the obtained data
        :return: Generator of the YoutubeVideo
        """
        if sources is None:
            sources = self.__sources
        for i, source in enumerate(sources):
            print(f'\r{i + 1}/{len(sources)}\tDownloading info from {source}', end='')
            for source_info in self.get_source_info(source, limit=limit, order=order):
                yield source_info
        print('\r ', end='')
        print('\r', end='')

    def _get_video_ids(
            self,
            channel_id: str,
            limit: int = __DEFAULT_INFO_LIMIT,
            order: SearchOrder = SearchOrder.DATE,
            page_token: str = '') -> Response:
        url = self.__query_builder(func='search', pars={
            'part': 'snippet',
            'channelId': channel_id,
            'maxResults': min(limit, self.__INFO_BATCH_SIZE),
            'order': order.value,
            'type': 'video',
            'pageToken': page_token
        })
        req = requests.get(url)
        result = YoutubeShell.__parse(req, YoutubeShell.__parse_video_ids)
        if result.code == ResponseCode.ERROR:
            result.content['message'] = 'failed to find videos on ' + channel_id
        elif result.code == ResponseCode.OK:
            rest_limit = limit - self.__INFO_BATCH_SIZE
            if rest_limit > 0:
                next_page_token = req.json().get('nextPageToken', None)
                if next_page_token is not None:
                    next_page = self._get_video_ids(
                        channel_id=channel_id,
                        limit=rest_limit,
                        order=order,
                        page_token=next_page_token
                    )
                    if next_page.code == ResponseCode.OK:
                        result.content['result'].extend(next_page.content['result'])
        return result

    @staticmethod
    def __parse_video_ids(response_json: Dict) -> List[YoutubeVideo]:
        return [json_elem['id']['videoId'] for json_elem in response_json['items']]

    @classmethod
    def get_channel_id(cls, suffix: str) -> Response:
        """:param suffix: part after youtube.com/ (e.g., user/... or c/...)"""
        url = 'https://www.youtube.com/' + suffix
        req = requests.get(url, 'html.parser')
        if not req.ok:
            return Response(code=ResponseCode.ERROR, content={
                'message': f'failed to fetch the source at {url}',
                'response.status_code': str(req.status_code),
                'response.reason': req.reason
            })
        text = req.text
        loc = text.find('externalId')
        if loc == -1:
            return Response(code=ResponseCode.ERROR, content={'message': 'failed to find key identifier (externalId) on ' + suffix})
        return Response(code=ResponseCode.OK, content={'result': text[loc + cls.__CHID_OFFSET_FROM: loc + cls.__CHID_OFFSET_TO]})

    @staticmethod
    def __parse(response: requests.Response, parser: Callable) -> Response:
        if not response.ok:
            return Response(
                code=ResponseCode.ERROR,
                content={'response.status_code': str(response.status_code),
                         'response.reason': response.reason})
        try:
            js = response.json()
            parsed = Response(code=ResponseCode.OK, content={'result': parser(js)})
            return parsed
        except Exception as e:
            return Response(code=ResponseCode.PARSE_ERROR, content={'message': str(e), 'response.text': response.text})

    def _get_videos_info(self, videos: List[str]) -> Response:
        part = ','.join([
            'statistics',
            'contentDetails',
            'id',
            'liveStreamingDetails',
            'localizations',
            'player',
            'recordingDetails',
            'snippet',
            'status',
            'topicDetails'
        ])
        result = None
        for i in range(0, len(videos), self.__DEFAULT_INFO_LIMIT):
            ids = ','.join(videos[i:min(len(videos), i + self.__DEFAULT_INFO_LIMIT)])
            url = self.__query_builder(func='videos', pars={'part': part, 'id': ids})
            req = requests.get(url, headers=self.common_headers)
            batch_result = self.__parse(req, self.__parse_video_info)
            if batch_result.code != ResponseCode.OK:
                return batch_result
            if result is None:
                result = batch_result
            else:
                result.content['result'].extend(batch_result.content['result'])
        return result

    @staticmethod
    def __parse_video_info(request_json: Dict) -> List[YoutubeVideo]:
        return list(map(YoutubeVideo.from_get_response, request_json['items']))
