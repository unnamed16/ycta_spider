__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/28'

from typing import Any, Callable

import requests

from highlight_comment.api.shell import Shell as CommonShell, Comments
from highlight_comment.api.shell import PlatformType, ResponseCode
from highlight_comment.api.shell import SourceUri, CommentsResponse


class Shell(CommonShell):

    def __init__(self):
        super().__init__()
        self.__platform_type = PlatformType.YOUTUBE
        self.__url = 'https://www.googleapis.com/youtube/v3/'
        platform_config = self.config['platforms'][self.platform_type.name]
        self.__api_key = platform_config['api_key']
        self.__access_token = platform_config['access_token']

    def get_comments(self, source: SourceUri) -> CommentsResponse:
        func = 'commentThreads'
        part = 'part=snippet,replies'
        query = f'{self.__url}{func}?{part}&{source}&key={self.__api_key}'
        comments = requests.get(query, headers=self.common_headers)
        return Shell.__parse(comments, Shell.__parse_comments)

    def add_comment(self, source: SourceUri, comment: str) -> ResponseCode:
        func = 'commentThreads'
        part = 'part=snippet'
        query = f'{self.__url}{func}?{part}&key={self.__api_key}'
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

    @staticmethod
    def get_authorization_link() -> str:
        return \
            "https://accounts.google.com/o/oauth2/v2/auth?" \
            "client_id=462864845006-vb4h8144a0jdkee7810bvluov1nrnoip.apps.googleusercontent.com&response_type=code&" \
            "scope=https://www.googleapis.com/auth/youtube.force-ssl&" \
            "access_type=offline&" \
            "redirect_uri=urn:ietf:wg:oauth:2.0:oob"

    @staticmethod
    def get_access_token(authorization_code: str) -> str:
        access_token = requests.post("https://www.googleapis.com/oauth2/v4/token", data={
            "client_id": "462864845006-vb4h8144a0jdkee7810bvluov1nrnoip.apps.googleusercontent.com",
            "client_secret": "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",
            "code": authorization_code,
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
            "grant_type": "authorization_code"
        })
        return access_token.text
