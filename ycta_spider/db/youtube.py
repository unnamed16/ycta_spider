__licence__ = 'MIT'
__author__ = 'pvp'
__credits__ = ['pvp']
__maintainer__ = 'pvp'
__date__ = '2022/07/17'

from typing import Iterable

from ycta_spider.structures.youtube import YoutubeVideo, YoutubeChannel, PrimaryComment, SecondaryComment
from ycta_spider.db.common import PsqlConnector
from ycta_spider.structures.common import Source

def send_info(info: Iterable[Source], table: str):
    """store youtube-related data in the DB

    :param info: iterable object with info represented via dataclass
    :param table: table that's matched with the input type, should be video_info, channel_info or comments
    """
    with YoutubePsqlConnector() as conn:
        if table == "video_info":
            conn.add_video_info(info)
        elif table == "channel_info":
            conn.add_channel_info(info)
        elif table == "primary_comment":
            conn.add_primary_comments(info)
        elif table == "secondary_comment":
            conn.add_secondary_comments(info)


class YoutubePsqlConnector(PsqlConnector):
    """Use to create and interact with the DB tables of the Youtube DB.
    Use via the context syntax, to ensure that no outstanding connections are left hanging."""
    __table_creation_query = """
        create table video_info
        (
            idx              char(11) not null,
            time             timestamptz not null,
            publish_time     timestamptz not null,
            channel_id       char(24) not null,
            title            text,
            description      text,
            duration         varchar(12),
            channel_title    text,
            tags             text[],
            category_id      int,
            view_count       int,
            like_count       int,
            comment_count    int,
            topic_categories text[]
        );

        create unique index video_info_idx_uindex
            on video_info (idx);
    """
    __db = 'youtube'
    __cols = YoutubeVideo.psql_cols()

    def add_video_info(self, info: Iterable[YoutubeVideo]):
        """add entries from the info object to the video_info table in one query.
        Inserts on first entry, updates on conflicts."""
        self.run_query(
            "INSERT INTO video_info (" +
            ", ".join(self.__cols) +
            ") VALUES " +
            ", ".join([entry.psql_to_value(self.__cols) for entry in info]) +
            " ON CONFLICT (idx) DO UPDATE SET " +
            ", ".join([f'{key} = excluded.{key}' for key in self.__cols]) +
            ';'
        )

    def add_channel_info(self, info: Iterable[YoutubeChannel]):
        raise NotImplementedError  # TODO

    def add_primary_comments(self, info: Iterable[PrimaryComment]):
        raise NotImplementedError  # TODO

    def add_secondary_comments(self, info: Iterable[SecondaryComment]):
        raise NotImplementedError  # TODO