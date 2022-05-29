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
        self.__platform_type = PlatformType.TELEGRAM
        # todo: change url
        self.host = 'https://developers.google.com/apis-explorer/#p/youtube/v3/'
        self.access_key = self.config['platforms'][self.platform_type.name]['access_key']
        self.secret_key = self.config['platforms'][self.platform_type.name]['secret_key']

    def get_comments(self, source: SourceUri) -> CommentsResponse:
        # todo: change url
        url = 'youtube.commentThreads.list'
        part = 'part=snippet,replies'
        comments = requests.get(f'{self.host}{url}?{part}&{source}')
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
