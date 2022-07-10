import os
from csv import reader, writer

from ycta_spider.file_manager.reader import read_config
from ycta_spider.structures.youtube import Channel, Channels

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
