__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/06/01'

import json
from pathlib import Path
from typing import Union, Iterable

from highlight_comment.api.shell import Comments
from highlight_comment.file_manager.writer import save_json, save_csv
from highlight_comment.structures.common import SourceInfo


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
        print(f'Source Info #{i}:\n')
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
    save_csv(
        (
            source_info.__dict__.values()
            for source_info in info
        ),
        path
    )
