__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/27'

from abc import ABC
from typing import Iterator, List, Iterable, Any

from ycta_spider.file_manager.reader import read_config
from ycta_spider.structures.common import PlatformType, Comment, Source, Response, Responses
from ycta_spider.structures.youtube import SearchOrder


class Shell(ABC):
    __INFO_CONTINUOUS_DELAY = 900    # seconds
    __COMMENTS_CONTINUOUS_DELAY_FRESH = 60    # every minute
    __COMMENTS_CONTINUOUS_DELAY_MEDIUM = 900  # every 15 minutes
    __COMMENTS_CONTINUOUS_DELAY_RARE = 43200  # twice daily
    __COMMENTS_FRESH_RANGE = 3600    # hour in seconds
    __COMMENTS_MEDIUM_RANGE = 86400  # day in seconds
    __COMMENTS_RARE_RANGE = 2592000  # month

    def __init__(self):
        self.common_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.config = read_config()
        self._platform_type = None

    @property
    def platform_type(self) -> PlatformType:
        return self._platform_type

    def get_source_info(self, source: str, *args, **kwargs) -> Response:
        """
        Return info for the specified source or sub sources if the source is not a leaf\n
        :param source: description of the source where from the comments have to be obtained
        :return: result of the operation, which equals
        """
        pass

    def get_sources_info(self, sources: Iterable[Any], *args, **kwargs) -> Iterable[Any]:
        """
        Return info for the several specified sources\n
        :param sources: source descriptions list for which the info has to be obtained
        :return: results of the
        """
        pass

    def get_sources_info_continuous(self, sources: Iterable[Any]) -> Responses:
        """
        Return info for the several specified sources and update it continuously\n
        :param sources: source descriptions list for which the info has to be obtained
        :return: responses
        """
        pass

    def get_comments(self, source: Any, limit: int, order: SearchOrder) -> Iterator[Comment]:
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
            sources: List[Any],
            limit: int,
            order: SearchOrder) -> Responses:
        """
        Return all comments for the several specified sources\n
        :param sources: source descriptions list where from the comments have to be obtained
        :param limit: limit of the comments to download from each source
        :param order: sort order of the obtained data
        :return: Generator of the Comments
        """
        pass

    def get_comments_from_several_sources_continuous(
            self,
            sources: List[Any],
            limit: int,
            order: SearchOrder) -> Response:
        """
        Return all comments for the several specified sources and update it continuously\n
        :param sources: source descriptions list where from the comments have to be obtained
        :param limit: limit of the comments to download from each source
        :param order: sort order of the obtained data
        :return: Generator of the Comments
        """
        pass

    def add_comment(self, source: Source, comment: str) -> Response:
        """
        Add specified comment to the source (it may be video, channel or another comment)\n
        :param source: description of the source where the comment has to be placed
        :param comment: text that has to be added
        :return: result of the operation
        """
        pass
