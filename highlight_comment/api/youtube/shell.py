__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/28'

import datetime as dt
from typing import Any, Callable, Dict, List
from enum import Enum
from dataclasses import dataclass
import json
from dateutil.parser import isoparse

import requests

from highlight_comment.api.shell import Shell as CommonShell
from highlight_comment.api.shell import PlatformType, ResponseCode
from highlight_comment.api.shell import SourceUri, Response, Comments, Comment


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


class Shell(CommonShell):
    __CHID_OFFSET_FROM = 13
    __CHID_OFFSET_TO = 37
    __V3_URL = 'https://www.googleapis.com/youtube/v3/'
    __OAUTH2_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    __SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
    __REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
    __TOKEN_URL = "https://www.googleapis.com/oauth2/v4/token"

    def __init__(self):
        super().__init__()
        self.__platform_type = PlatformType.YOUTUBE
        platform_config = self.config['platforms'][self.platform_type.name]
        self.__api_key = platform_config['api_key']
        self.__client_id = platform_config['client_id']
        self.__client_secret = platform_config['client_secret']
        self.__access_token = platform_config['access_token']

    def get_comments(self, source: SourceUri) -> Response:
        func = 'commentThreads'
        part = 'snippet,replies'
        query = f'{self.__V3_URL}{func}?part={part}&{source}&key={self.__api_key}'
        comments = requests.get(query, headers=self.common_headers)
        return Shell.__parse(comments, Shell.__parse_comments)

    def add_comment(self, source: SourceUri, comment: str) -> Response:
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
        return Shell.__parse(comments, Shell.__parse_comments)

    @staticmethod
    def __parse_comments(response_json: Dict) -> Comments:
        # todo: finish parser
        return response_json

    @staticmethod
    def __parse_video_ids(response_json: Dict) -> List[VideoData]:
        return [
            VideoData(
                videoId=json_elem['id']['videoId'],
                publishedAt=isoparse(json_elem['snippet']['publishedAt']),
                title=json_elem['snippet']['title'],
                description=json_elem['snippet']['description']
            )
            for json_elem in response_json['items']
        ]

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

    def get_video_ids(self, channel_id: str, max_results: int, order: SearchOrder) -> Response:
        part = 'snippet'
        content_type = 'video'
        func = 'search'
        url = str(
            f'{self.__V3_URL}{func}?'
            f'part={part}&'
            f'channelId={channel_id}&'
            f'maxResults={max_results}&'
            f'order={order.value}&'
            f'type={content_type}&'
            f'key={self.__api_key}'
        )
        req = requests.get(url)
        result = Shell.__parse(req, Shell.__parse_video_ids)
        if result['code'] == ResponseCode.ERROR:
            result['message'] = f'failed to find videos on {channel_id}'
        return result

    @classmethod
    def get_channel_id(cls, channel: str) -> Response:
        url = f'https://www.youtube.com/c/{channel}'
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
                'message': f'failed to find key identifier (externalId) on {channel}'
            }
        return {
            'code': ResponseCode.OK,
            'result': text[loc + cls.__CHID_OFFSET_FROM: loc + cls.__CHID_OFFSET_TO]
        }
