__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/06/01'

from typing import Any

from highlight_comment.api.shell import Comments
from highlight_comment.file_manager.writer import save_json


def print_comments(comments: Comments, manual_control: bool = False) -> None:
    """
    Print Comments to the stdio
    :param comments: Iterable Comments
    :param manual_control: wait input before obtaining next record if True
    """
    for comment in comments:
        print(f'{comment}')
        print('')


def save_comments(comments: Comments, path: Any) -> None:
    save_json(comments, path)
