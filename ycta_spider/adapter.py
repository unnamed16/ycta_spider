__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/06/01'

from ycta_spider.db.build import info_senders
from ycta_spider.file_manager.writer import save_json, save_csv
from ycta_spider.structures.common import Comments, Sources, Info


def print_comments(comments: Comments, manual_control: bool = False) -> None:
    """
    Print Comments to the stdio
    :param comments: Iterable Comments
    :param manual_control: wait input before obtaining next record if True
    """
    for i, comment in enumerate(comments):
        print(f'Comment #{i}:\n{comment}')
        if manual_control:
            input()


def print_info(sources: Sources, manual_control: bool = False) -> None:
    """
    Print Sources Info to the stdio
    :param sources: Iterable Sources Info
    :param manual_control: wait input before obtaining next record if True
    """
    for i, source_info in enumerate(sources):
        print(f'\nSource Info #{i}:\n')
        print('\n'.join(f'\t{key} = {val}' for key, val in source_info.__dict__.items()))
        if manual_control:
            input()


def save_comments(comments: Comments, path: str) -> None:
    """
    Save Comments to file (csv or json)
    :param comments: Iterable Comments
    :param path: string with the path to an output file
    """
    if path.endswith('.csv'):
        save_csv(
            data=[
                [
                    ' '.join([f'{ids_key}={ids_value}' for ids_key, ids_value in comment['ids'].items()]),
                    comment['text'],
                    ' '.join([f'{meta_key}={meta_value}' for meta_key, meta_value in comment['meta'].items()]),
                    comment['likes'], len(comment.get('replies', ''))
                ]
                for comment in comments
            ],
            path=path,
            headers=comments[0]
        )
    elif path.endswith('.json'):
        save_json([comment.__dict__ for comment in comments], path)
    else:
        raise AttributeError('path should be either csv or json')


def save_info(sources: Sources, path: str) -> None:
    """
    Save Sources Info to file (csv only)
    :param sources: Iterable Sources Info
    :param path: string with the path to an output file
    """
    save_csv(data=sources, path=path)


def send_info(info: Info, path: str) -> None:
    """
    Save Sources Info (including comments)

    :param info: Iterable Sources Info
    :param path: '::'-separated triple (storage type, platform, table name), e.g.
        db::youtube::video_info
    """
    storage_type, platform, table = path.split('::')
    if storage_type == 'db':
        info_senders[platform.lower()](info, table)
    else:
        raise NotImplementedError


def send_comments(comments: Comments, path: str) -> None:
    """
    Save Comments
    :param comments: Iterable Comments
    :param path: string with the URL to DB
    """
    send_info(comments, path)
