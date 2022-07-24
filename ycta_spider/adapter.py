__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/06/01'

import json
from pathlib import Path
from typing import Union, Iterable

from ycta_spider.api.shell import Comments
from ycta_spider.file_manager.writer import save_json, save_csv
from ycta_spider.structures.common import SourceInfo
from ycta_spider.db.youtube import send_info as yt_store_info


def print_comments(comments: Comments, manual_control: bool = False) -> None:
    """
    Print Comments to the stdio
    :param comments: Iterable Comments
    :param manual_control: wait input before obtaining next record if True
    """
    for i, comment in enumerate(comments):
        print(f'Comment #{i}:\n{json.dumps(comment, indent=4, ensure_ascii=False)}')
        if manual_control:
            input()


def print_info(info: Iterable[SourceInfo], manual_control: bool = False) -> None:
    """
    Print Sources Info to the stdio
    :param info: Iterable Sources Info
    :param manual_control: wait input before obtaining next record if True
    """
    for i, source_info in enumerate(info):
        print(f'\nSource Info #{i}:\n')
        print('\n'.join(f'\t{key} = {val}' for key, val in source_info.__dict__.items()))
        if manual_control:
            input()


def save_comments(comments: Comments, path: Union[str, Path]) -> None:
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
            headers=('ids', 'text', 'meta', 'likes', 'replies')
        )
    else:
        save_json(list(comments), path)


def save_info(info: Iterable[SourceInfo], path: Union[str, Path]) -> None:
    """
    Save Sources Info to file (csv only)
    :param info: Iterable Sources Info
    :param path: string with the path to an output file
    """
    info = list(info)  # TODO: this will take additional memory, we can make it much more effective if not use list.
    data = [
        source_info.__dict__.values()
        for source_info in info
    ]
    headers = info[0].__dict__.keys() if info else []  # TODO: this may work not proper if there are different headers
    save_csv(
        data=data,
        path=path,
        headers=headers
    )


def send_info(info: Iterable[SourceInfo], platform: str, table: str) -> None:
    """
    Save Sources Info to DB
    :param info: Iterable Sources Info

    :param table: pick the right table for the source info type
    """
    if platform == 'youtube':
        yt_store_info(info, table)
    else:
        raise NotImplementedError  # TODO


def send_comments(comments: Comments, path: Union[str, Path]) -> None:
    """
    Save Comments to DB (by URL)
    :param comments: Iterable Comments
    :param path: string with the URL to DB
    """
    # TODO: implement database communication
    for i, comment in enumerate(comments):
        print(f'\nComment #{i}:\n')
        print('\n'.join(f'\t{key} = {val}' for key, val in comment.items()))
