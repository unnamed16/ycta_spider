__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/03/22'

from highlight_comment.api.shell import Comments
from highlight_comment.file_manager.writer import save_json


def print_comments(comments: Comments) -> None:
    for comment in comments:
        print(f'{comment}')
        print('')


def save_comments(comments: Comments) -> None:
    save_json(comments)
