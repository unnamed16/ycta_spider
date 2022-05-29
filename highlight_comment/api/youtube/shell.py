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

from highlight_comment.api.shell import Shell as CommonShell, Comments
from highlight_comment.api.shell import PlatformType, ResponseCode
from highlight_comment.api.shell import SourceUri, CommentsResponse


class Shell(CommonShell):
    __CHID_OFFSET_FROM = 13
    __CHID_OFFSET_TO = 37
    __CLIENT_ID = "462864845006-vb4h8144a0jdkee7810bvluov1nrnoip.apps.googleusercontent.com"
    __CLIENT_SECRET = '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'
    __V3_URL = 'https://www.googleapis.com/youtube/v3/'
    __OAUTH2_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    __SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
    __REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
    __TOKEN_URL = "https://www.googleapis.com/oauth2/v4/token"

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

    def __init__(self):
        super().__init__()
        self.__platform_type = PlatformType.YOUTUBE
        platform_config = self.config['platforms'][self.platform_type.name]
        self.__api_key = platform_config['api_key']
        self.__access_token = platform_config['access_token']

    def get_comments(self, source: SourceUri) -> CommentsResponse:
        func = 'commentThreads'
        part = 'snippet,replies'
        query = f'{self.__V3_URL}{func}?part={part}&{source}&key={self.__api_key}'
        comments = requests.get(query, headers=self.common_headers)
        return Shell.__parse(comments, Shell.__parse_comments)

    def add_comment(self, source: SourceUri, comment: str) -> CommentsResponse:
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
    def __parse_comments(comments) -> Comments:
        # todo: finish parser
        return comments

    @staticmethod
    def __parse(r: requests.Response, parser: Callable) -> CommentsResponse:
        try:
            js = r.json()
            parsed = {
                'result': parser(js),
                'code': ResponseCode.OK
            }
            return parsed
        except Exception as e:
            return {
                'code': ResponseCode.ERROR,
                'message': str(e),
                'response.text': r.text
            }

    @classmethod
    def get_authorization_link(cls) -> str:
        return \
            f"{cls.__OAUTH2_URL}?client_id={cls.__CLIENT_ID}&response_type=code&scope={cls.__SCOPE}&" \
            f"access_type=offline&redirect_uri={cls.__REDIRECT_URI}"

    @classmethod
    def get_access_token(cls, authorization_code: str) -> Dict:
        access_token = requests.post(cls.__TOKEN_URL, data={
            "client_id": cls.__CLIENT_ID,
            "client_secret": cls.__CLIENT_SECRET,
            "code": authorization_code,
            "redirect_uri": cls.__REDIRECT_URI,
            "grant_type": "authorization_code"
        })
        return json.loads(access_token.text)

    def get_video_ids(self, channel_id: str, max_results: int, order: SearchOrder) -> Dict[str, Any]:
        part = 'snippet'
        content_type = 'video'
        func = 'search'
        url = f'{self.__V3_URL}{func}?part={part}&channelId={channel_id}&maxResults={max_results}&' \
              f'order={order.value}&type={content_type}&key={self.__api_key}'
        req = requests.get(url)
        if not req.ok:
            return {
                'code': ResponseCode.ERROR,
                'message': f'failed to find videos on {channel_id}',
                'response.status_code': str(req.status_code),
                'response.reason': req.reason
            }
        json_content = json.loads(req.text)
        video_list = []
        for json_elem in json_content['items']:
            video_list.append(self.VideoData(
                videoId=json_elem['id']['videoId'],
                publishedAt=isoparse(json_elem['snippet']['publishedAt']),
                title=json_elem['snippet']['title'],
                description=json_elem['snippet']['description']
            ))
        return {'code': ResponseCode.OK, 'result': video_list}

    @classmethod
    def get_channel_id(cls, channel: str) -> Dict[str, Any]:
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
