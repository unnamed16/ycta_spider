import os
from csv import reader, writer
from typing import Iterable

import psycopg2

from ycta_spider.file_manager.reader import read_config
from ycta_spider.structures.youtube import Channel, Channels, VideoInfo
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


def store_info(info: Iterable[SourceInfo], table: str):
    if table == "video_info":
        with YoutubePsqlConnector() as conn:
            conn.add_video_info(info)
    else:
        raise NotImplementedError  # TODO channel & comment


class YoutubePsqlConnector:
    _VIDEO_INFO_TABLE_CREATION_QUERY = """
        create table video_info
        (
            idx              char(11) not null,
            time             timestamptz not null,
            title            text,
            description      text,
            duration         varchar(12),
            channel_id       char(24) not null,
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
    """  # when testing, run once to create a table locally
    _DB = 'youtube'

    def __init__(self, config=None):
        if config is None:
            config = read_config()
        self._psql_config = config['psql']
        self._connector = None

    def __enter__(self):
        self._connector = psycopg2.connect(database=self._DB, **self._psql_config)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._connector.commit()
        self._connector.close()
        self._connector = None

    def run_query(self, query: str):
        assert self._connector is not None, "initialize using with context"
        with self._connector.cursor() as cur:
            cur.execute(query)

    def add_video_info(self, info: Iterable[VideoInfo]):
        query = f'INSERT INTO video_info ' \
                f'(idx, time, title, description, duration, channel_id, channel_title, tags, ' \
                f'category_id, view_count, like_count, comment_count, topic_categories) VALUES '
        isnt_first = False
        for entry in info:
            if isnt_first:
                query += ','
            tag_list = "'{\"" + '","'.join(entry.tags) + "\"}'"
            topic_list = "'{\"" + '","'.join(entry.topic_categories) + "\"}'"
            query += f"('{entry.idx}', '{entry.time}', '{entry.title}', '{entry.description}', '{entry.duration}', " \
                   f"'{entry.channel_id}', '{entry.channel_title}', {tag_list}, {entry.category_id}, " \
                   f"{entry.view_count}, {entry.like_count}, {entry.comment_count}, {topic_list})"
            isnt_first = True
        query += ';'
        self.run_query(query)