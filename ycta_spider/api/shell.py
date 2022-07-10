__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/27'

from enum import Enum
from typing import Tuple, Dict, Union, Any, Iterator, List

from ycta_spider.file_manager.reader import read_config
from ycta_spider.structures.common import SourceInfo


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


class SearchOrder(Enum):
    DATE = 'date'
    TIME = 'time'
    RATING = 'rating'
    RELEVANCE = 'relevance'
    TITLE = 'title'
    VIDEO_COUNT = 'videoCount'
    VIEW_COUNT = 'viewCount'


Source = Tuple[str, Any]  # TODO: Make it a datastructure
NumLikes = int
VideoId = str
ThreadId = str
CommentId = str
MetaInfo = Dict[str, Union[bool, None, CommentId, int, str]]
Ids = Tuple[VideoId, ThreadId, CommentId]
Comment = Dict[str, Union[Source, CommentId, str, MetaInfo, NumLikes, List]]
Comments = Iterator[Comment]
Response = Dict[str, Any]


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

    def get_source_info(self, source: Source, limit: int, order: SearchOrder) -> Iterator[SourceInfo]:
        """
        Return info for the specified source or sub sources if the source is not a leaf\n
        :param source: description of the source where from the comments have to be obtained
        :param limit: limit of the sub-sources to process
        :param order: sort order of the obtained data
        :return: Generator of the SourceInfo
        """
        pass

    def get_sources_info(self, sources: List[Source], limit: int, order: SearchOrder) -> Iterator[SourceInfo]:
        """
        Return info for the several specified sources\n
        :param sources: source descriptions list for which the info has to be obtained
        :param limit: limit of the sources obtained from each source
        :param order: sort order of the obtained data
        :return: Generator of the SourceInfo
        """
        pass

    def get_sources_info_continuous(
            self,
            sources: List[Source],
            limit: int,
            order: SearchOrder) -> Iterator[SourceInfo]:
        """
        Return info for the several specified sources and update it continuously\n
        :param sources: source descriptions list for which the info has to be obtained
        :param limit: limit of the sources obtained from each source
        :param order: sort order of the obtained data
        :return: Generator of the SourceInfo
        """
        pass

    def get_comments(self, source: Source, limit: int, order: SearchOrder) -> Iterator[Comment]:
        """
        Return all comments for the specified source\n
        :param source: description of the source where from the comments have to be obtained
        :param limit: limit of the comments to download
        :param order: sort order of the obtained data
        :return: List of the Comments
        """
        pass

    def get_comments_from_several_sources(
            self,
            sources: List[Source],
            limit: int,
            order: SearchOrder) -> Iterator[Comment]:
        """
        Return all comments for the several specified sources\n
        :param sources: source descriptions list where from the comments have to be obtained
        :param limit: limit of the comments to download
        :param order: sort order of the obtained data
        :return: List of the Comments
        """
        pass

    def add_comment(self, source: Source, comment: str) -> Comment:
        """
        Add specified comment to the source (it may be video, channel or another comment)\n
        :param source: description of the source where the comment has to be placed
        :param comment: text that has to be added
        :return: added Comment
        """
        pass
