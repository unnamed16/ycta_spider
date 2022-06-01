import os
from _csv import reader, writer

from highlight_comment.file_manager.reader import read_config
from highlight_comment.structures.youtube import Channel, Channels

ID_SUFFIXES = ['c', 'channel', 'user']


class ChannelCache:
    @staticmethod
    def cache_path():
        return os.path.join(read_config()['data_path'], 'youtube')

    @classmethod
    def load_channels(cls) -> Channels:
        channels = []
        with open(os.path.join(cls.cache_path(), 'channels.csv'), newline='') as csvfile:
            spamreader = reader(csvfile, delimiter=',', quotechar='|')
            next(spamreader)
            for (id, id_suff, is_antiput, desc) in spamreader:
                suff = ID_SUFFIXES[int(id_suff)]
                ch_kwargs = {'name': id, 'is_antiput': int(is_antiput), 'suffix': suff, 'desc': desc}
                if suff == 'channel':
                    ch_kwargs['channelId'] = id
                channels.append(Channel(**ch_kwargs))
        return channels

    @classmethod
    def add_channels(cls, name: str, is_antiput: int, suffix: str, desc: str):
        with open(os.path.join(cls.cache_path(), 'channels.csv'), 'a', newline='') as f:
            writer(f).writerow([name, ID_SUFFIXES.index(suffix), is_antiput, desc])
