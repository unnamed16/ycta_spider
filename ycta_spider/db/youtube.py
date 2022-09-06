__licence__ = 'MIT'
__author__ = 'pvp'
__credits__ = ['pvp']
__maintainer__ = 'pvp'
__date__ = '2022/07/17'

from abc import ABC, abstractmethod
from functools import wraps
from typing import Iterable, List, Type

from ycta_spider.api.shell import PlatformType
from ycta_spider.db.common import PsqlTable
from ycta_spider.structures.common import Response, ResponseCode, GradedEntry
from ycta_spider.structures.youtube import YoutubeVideo, YoutubeChannel, YoutubePrimaryComment, \
    YoutubeSecondaryComment, YoutubeInfo


class YoutubeTable(PsqlTable, ABC):
    _db = 'youtube'

    @property
    @abstractmethod
    def _youtube_structure(self) -> Type[GradedEntry]:
        pass

    @property
    @abstractmethod
    def _youtube_structure(self) -> Type[GradedEntry]:
        pass

    @property
    def _cols(self) -> List[str]:
        return self._youtube_structure.columns  # noqa

    @classmethod
    def add_info(cls, info: YoutubeInfo) -> Response:
        """
        :param info: iterable with elements that match the table's contents
        :return: successfulness of the operation
        """
        with cls() as conn:
            query = (
                    f"INSERT INTO {cls._name} ("
                    + ", ".join(conn._cols)  # noqa
                    + ") VALUES "
                    + ", ".join([entry.to_query_vals() for entry in info])
                    + " ON CONFLICT (idx) DO UPDATE SET "
                    + ", ".join([f'{key} = excluded.{key}' for key in conn._cols])  # noqa
                    + ';'
            )
            try:
                conn.run_query(query)
                return Response(code=ResponseCode.OK)
            except Exception as e:
                return Response(code=ResponseCode.ERROR, content={'message': str(e), 'psql_query': query})

    @classmethod
    def get_info_by_idxs_with_failure(cls, idxs: Iterable[str]) -> YoutubeInfo:
        """
        :param idxs: list of indexes
        :return: list with info, if successful, fail hard otherwise
        """
        with cls() as conn:
            query = f"SELECT " + ", ".join(conn._cols) + f" FROM {cls._name} WHERE idx IN ('" + "', '".join(
                idxs) + "');"
            return [cls._youtube_structure.inst_from_psql_output(vals)  # noqa
                    for vals in conn.run_query(query)]

    @classmethod
    def get_info_by_idxs(cls, idxs: Iterable[str]) -> Response:
        """
        :param idxs: list of indexes
        :return: response with info in case of success, or cause of failure
        """
        with cls() as conn:
            query = f"SELECT " + ", ".join(conn._cols) + f" FROM {cls._name} WHERE idx IN ('" + "', '".join(
                idxs) + "');"
            try:
                return Response(code=ResponseCode.OK, content={'result': [
                    cls._youtube_structure.inst_from_psql_output(vals)  # noqa
                    for vals in conn.run_query(query)
                ]})
            except Exception as e:
                return Response(code=ResponseCode.ERROR, content={'message': str(e), 'psql_query': query})


def _comments_creation_query_common(table: str, idx_len: int) -> str:
    return f"""
            create table if not exists {table}
        (
            idx                 char({idx_len})                 not null
                constraint {table}_pkey
                    primary key,
            time                timestamp with time zone not null,
            grade               real                     not null,
            grade_confidence    real                     not null,
            text                varchar(10000)           not null,
            access_count        integer                  not null,
            text_original       varchar(10000)           not null,
            etag                char(27)                 not null,
            author_display_name varchar(100)             not null,
            author_channel_id   char(24)                 not null,
            author_profile_image_url  varchar(200),
            like_count          integer                  not null,
            published_at        timestamp with time zone not null,
            updated_at          timestamp with time zone not null
    """


class YoutubePrimaryCommentTable(YoutubeTable):
    _name = 'primary_comments'
    _table_creation_query = _comments_creation_query_common(_name, 26) + f""",
            video_id            char(11)                 not null,
            total_reply_count   integer                  not null,
            children_idx_suff   char(22)[]
        );
        
        comment on table {_name} is 'top-level comments (thread-starters)';
    """
    _youtube_structure = YoutubePrimaryComment


class YoutubeSecondaryCommentTable(YoutubeTable):
    _name = 'secondary_comments'
    _table_creation_query = _comments_creation_query_common(_name, 49) + f""");

        comment on table {_name} is 'replies to top-level comments';
    """
    _youtube_structure = YoutubeSecondaryComment


class YoutubeVideoTable(YoutubeTable):
    _name = 'video_info'

    _table_creation_query = f"""
            create table if not exists {_name}
        (
            idx                 char(11)                 not null
                constraint {_name}_pkey
                    primary key,
            time                timestamp with time zone not null,
            grade               real                     not null,
            grade_confidence    real                     not null,
            access_count        integer                  not null,
            etag                char(27)                 not null,
            published_at        timestamp with time zone not null,
            channel_id          char(24)                 not null,            
            title               varchar(100)             not null,
            description         varchar(5000)            not null,
            duration            real                     not null,
            category_id         integer                  not null,
            view_count          integer                  not null,
            like_count          integer                  not null,
            comment_count       integer                  not null,
            tags                text[][]                 not null,
            topic_categories    text[][]                 not null
        );
        
        comment on table {_name} is 'video meta data';

    """
    _youtube_structure = YoutubeVideo


class YoutubeChannelTable(YoutubeTable):
    _name = 'channel_info'
    _table_creation_query = f"""
            create table if not exists {_name}
        (
            idx                 char(24)                 not null
                constraint {_name}_pkey
                    primary key,
            time                timestamp with time zone not null,
            grade               real                     not null,
            grade_confidence    real                     not null,
            access_count        integer                  not null,
            etag                char(27)                 not null,
            published_at        timestamp with time zone not null,            
            title               varchar(100)             not null,
            description         varchar(5000)            not null,
            view_count          bigint                   not null,
            subscriber_count    bigint                   not null,
            video_count         bigint                   not null,
            keywords            text[][]                 not null,
            country             varchar(3)               not null,
            topic_categories    text[][]                 not null
        );

        comment on table {_name} is 'meta-data on channels';
    """
    _youtube_structure = YoutubeChannel


__TABLE_STR_TO_CLASS = {
    'video_info': YoutubeVideoTable,
    'channel_info': YoutubeChannelTable,
    'primary_comments': YoutubePrimaryCommentTable,
    'secondary_comments': YoutubeSecondaryCommentTable
}


def __info_exch_error_msg(fun):
    @wraps(fun)
    def with_try(arg, table: str):
        try:
            return fun(arg, table)
        except KeyError:
            error_msg = f'table can be ' + ', '.join([str(k) for k in __TABLE_STR_TO_CLASS.keys()])
            return Response(code=ResponseCode.ERROR, content={'message': error_msg})

    return with_try


@__info_exch_error_msg
def send_info(info: YoutubeInfo, table: str) -> Response:
    """store youtube-related data in the DB

    :param info: iterable object with info represented via dataclass
    :param table: table that's matched with the input type, should be video_info, channel_info or comments
    :returns: result of the operation
    """
    return __TABLE_STR_TO_CLASS[table].add_info(info)


@__info_exch_error_msg
def get_info(idxs: Iterable[str], table: str) -> Response:
    """try to store youtube-related data in the DB

    :param idxs: fetch data by a list of indexes
    :param table: table that's matched with the input type, should be video_info, channel_info or comments
    :returns: result of the operation
    """
    return __TABLE_STR_TO_CLASS[table].get_info_by_idxs(idxs)


def load_primary_comment_key_data(comment_id: str) -> dict:
    """
    load the data sufficient for displaying a primary comment on the frontend.
    it is expected that the

    :param comment_id: string ID of the comment
    :returns: dictionary with key fields, if the primary comment and video info are already stored in the DB
    """
    comments = list(YoutubePrimaryCommentTable.get_info_by_idxs_with_failure([comment_id]))
    assert len(comments) == 1, f'comment with id {comment_id} was not found in the DB'
    comment = comments[0]

    video_id = comment.video_id
    videos = list(YoutubeVideoTable.get_info_by_idxs_with_failure([video_id]))
    assert len(videos) == 1, f'video with id {video_id} was not found in the DB'
    video = videos[0]
    return {
        'platform': PlatformType.YOUTUBE.value,
        'commentId': comment_id,
        'sourceId': video_id,
        'sourceInfo': video.title,
        'authorName': comment.author_display_name,
        'authorSrc': comment.author_profile_image_url,
        'text': comment.text,
        'date': comment.published_at.date(),
        'replies': comment.total_reply_count,
        'likes': comment.like_count,
        'sentiment': comment.grade,
    }
