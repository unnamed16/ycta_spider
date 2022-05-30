__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/27'

from enum import Enum
from typing import Tuple, List, Dict, Union, TypeVar

from highlight_comment.file_manager.reader import read_config


class PlatformType(Enum):
    VK = 'VK'
    YOUTUBE = 'YOUTUBE'
    TELEGRAM = 'TELEGRAM'


class ResponseCode(Enum):
    OK = 'OK'
    ERROR = 'ERROR'
    PARSE_ERROR = 'PARSE ERROR'
    UNKNOWN = 'UNKNOWN'
    TOO_FREQUENT = 'TOO FREQUENT'


SourceUri = str
CommentUri = str
Comment = Tuple[CommentUri, str]
Comments = List[Comment]
CommentsResponse = Dict[str, Union[ResponseCode, Comments]]
ResponseVar = TypeVar('ResponseVar')
Response = Dict[str, Union[ResponseCode, ResponseVar]]


class Shell:

    def __init__(self):
        self.common_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.config = read_config()
        self.__platform_type = None

    @property
    def platform_type(self) -> PlatformType:
        return self.__platform_type

    def get_comments(self, source: SourceUri) -> List[Comment]:
        """
        Return all comments for the specified source.
        :return: Dictionary with key 'balances' in the root and a corresponding dictionary with currencies as keys
        and pairs Available/Locked Balances as values.
        """
        pass

    def add_comment(self, source: SourceUri, comment: str) -> ResponseCode:
        """
        Add specified comment to the source:
        :param source: link to the source where the comment has to be placed.
        :param comment: text that has to be added.
        :return: response code from the api.
        """
        pass

    def add_response(self, comment: CommentUri, response: str) -> ResponseCode:
        """
        Add specified response to the comment:
        :param comment: link to the comment where the response has to be placed.
        :param response: text that has to be added.
        :return: response code from the api.
        """
        pass
