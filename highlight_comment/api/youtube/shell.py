__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/28'

from typing import Any, Callable, Optional

import requests

from highlight_comment.api.shell import Shell as CommonShell, Comments
from highlight_comment.api.shell import PlatformType, ResponseCode
from highlight_comment.api.shell import SourceUri, CommentsResponse


class Shell(CommonShell):
    _CHID_OFFSET_FROM = 13
    _CHID_OFFSET_TO = 37

    def __init__(self):
        super().__init__()
        self.__platform_type = PlatformType.YOUTUBE
        self.__host = 'https://www.googleapis.com/youtube/v3/'
        platform_config = self.config['platforms'][self.platform_type.name]
        self.__api_key = platform_config['api_key']
        self.__access_token = platform_config['access_token']
        self.__headers = dict(self.common_headers)

    def get_comments(self, source: SourceUri) -> CommentsResponse:
        url = 'commentThreads'
        part = 'part=snippet,replies'
        q = f'{self.__host}{url}?{part}&{source}&key={self.__api_key}'
        comments = requests.get(q, headers=self.__headers)
        return Shell.__parse(comments, Shell.__parse_comments)

    def add_comment(self, source: SourceUri, comment: str) -> ResponseCode:
        url = 'commentThreads'
        part = 'part=snippet'
        q = f'{self.__host}{url}?{part}&{source}&key={self.__api_key}'
        headers = dict(self.__headers)
        data = {
            "snippet": {
                "channelId": self.config['platforms'][self.platform_type.name]['channel_id'],
                "topLevelComment": {
                    "snippet": {
                        "textOriginal": f"{comment}"
                    }
                },
                "videoId": "i2FGXF540pU"
            }
        }
        headers['Authorization'] = f'Bearer {self.__access_token}'
        comments = requests.post(q, headers=headers, data=data)
        return Shell.__parse(comments, Shell.__parse_comments)

    @staticmethod
    def __parse_comments(comments) -> Comments:
        # todo: finish parser
        return comments

    @staticmethod
    def __parse(r: requests.Response, parser: Callable) -> Any:
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
    def get_channel_id(cls, channel: str) -> Optional[str]:
        url = f'https://www.youtube.com/c/{channel}'
        req = requests.get(url, 'html.parser')
        if req.status_code != 200:
            print(f'Failed to parse {url}')
            return None
        text = req.text
        loc = text.find('externalId')
        if loc == -1:
            print(f'Failed to find key identifier (externalId) on {channel}')
            return None
        return text[loc + cls._CHID_OFFSET_FROM: loc + cls._CHID_OFFSET_TO]
