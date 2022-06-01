__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/06/01'

import json
import re
from pathlib import Path
from typing import Union

from highlight_comment.api.shell import Comments
from highlight_comment.file_manager.writer import save_json, save_csv


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


def save_comments(comments: Comments, path: Union[str, Path]) -> None:
    if path.endswith('.csv'):
        save_csv(
            [
                [
                    ' '.join([
                        f'{ids_key}={ids_value}'
                        for ids_key, ids_value in comment['ids'].items()
                    ]),
                    re.sub('[^0-9a-zA-Zа-яА-Я]+', ' ', comment['text']),
                    ' '.join([
                        f'{meta_key}={meta_value}'
                        for meta_key, meta_value in comment['meta'].items()
                    ]),
                    comment['likes'],
                    len(comment.get('replies', ''))
                ]
                for comment in comments
            ],
            path
        )
    else:
        save_json(comments, path)
