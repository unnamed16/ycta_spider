__licence__ = 'MIT'
__author__ = 'pvp'
__credits__ = ['pvp']
__maintainer__ = 'pvp'
__date__ = '2022/07/17'

import os
from csv import reader, writer
from typing import Iterable

from ycta_spider.file_manager.reader import read_config
from ycta_spider.structures.youtube import Channel, Channels, VideoInfo, ChannelInfo, PrimaryComment, SecondaryComment
from ycta_spider.db.common import PsqlConnector
from ycta_spider.structures.common import SourceInfo

ID_SUFFIXES = ['c', 'channel', 'user']


class ChannelCache:
    @staticmethod
    def cache_path():
        return os.path.join(read_config()['data_path'], 'youtube')

    @classmethod
    def load_channels(cls) -> Channels:
        channels = []
        with open(os.path.join(cls.cache_path(), 'channels.csv'), newline='') as csvfile:
            spam_reader = reader(csvfile, delimiter=',', quotechar='|')
            next(spam_reader)
            for (idx, id_suffix, is_anti_put, desc) in spam_reader:
                suffix = ID_SUFFIXES[int(id_suffix)]
                ch_kwargs = {'name': idx, 'is_anti_put': int(is_anti_put), 'suffix': suffix, 'desc': desc}
                if suffix == 'channel':
                    ch_kwargs['channel_id'] = idx
                channels.append(Channel(**ch_kwargs))
        return channels

    @classmethod
    def add_channels(cls, name: str, is_anti_put: int, suffix: str, desc: str):
        with open(os.path.join(cls.cache_path(), 'channels.csv'), 'a', newline='') as f:
            writer(f).writerow([name, ID_SUFFIXES.index(suffix), is_anti_put, desc])


def send_info(info: Iterable[SourceInfo], table: str):
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
    _table_creation_query = """
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
    _db = 'youtube'
    _cols = VideoInfo.psql_cols()

    def add_video_info(self, info: Iterable[VideoInfo]):
        """add entries from the info object to the video_info table in one query.
        Inserts on first entry, updates on conflicts."""
        self.run_query(
            "INSERT INTO video_info (" +
            ", ".join(self._cols) +
            ") VALUES " +
            ", ".join([entry.psql_to_value(self._cols) for entry in info]) +
            " ON CONFLICT (idx) DO UPDATE SET " +
            ", ".join([f'{key} = excluded.{key}' for key in self._cols]) +
            ';'
        )

    def add_channel_info(self, info: Iterable[ChannelInfo]):
        raise NotImplementedError  # TODO

    def add_primary_comments(self, info: Iterable[PrimaryComment]):
        raise NotImplementedError  # TODO

    def add_secondary_comments(self, info: Iterable[SecondaryComment]):
        raise NotImplementedError  # TODO