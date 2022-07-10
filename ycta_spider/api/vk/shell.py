__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/28'

from typing import Any, Callable, Iterator

import requests

from ycta_spider.api.shell import Shell as CommonShell, Comments, SearchOrder, Comment
from ycta_spider.api.shell import PlatformType, ResponseCode
from ycta_spider.api.shell import Source


class Shell(CommonShell):

    def __init__(self):
        super().__init__()
        self.__platform_type = PlatformType.VK
        # todo: change url
        self.host = 'https://developers.google.com/apis-explorer/#p/youtube/v3/'

    def get_comments(self, source: Source, limit: int, order=SearchOrder.RELEVANCE) -> Iterator[Comment]:
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
