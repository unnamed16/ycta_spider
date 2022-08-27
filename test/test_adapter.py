__license__ = 'MIT'
__author__ = 'ppv'
__maintainer__ = 'ppv'
__date__ = '8/23/2022'

import unittest
import os
import pathlib
from unittest import mock
from ycta_spider import adapter
from ycta_spider.structures import common


class TestAdapter(unittest.TestCase):
    __path = str(pathlib.Path(__file__).parent.resolve())

    def test_print_comments(self):
        adapter.print_comments([common.Comment(idx='a', text='text')], manual_control=False)

    @mock.patch('builtins.print')
    def test_print_info(self, _):
        adapter.print_info([common.Source(idx='a', type='videoId')], manual_control=False)

    @mock.patch('ycta_spider.file_manager.writer.os.makedirs', new_callable=mock.mock_open)
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_save_comments(self, mock_makedirs, mock_open):
        path = os.path.join(self.__path, 'test.json')
        adapter.save_comments([common.Comment(idx='a', text='text')], path)

    def test_save_info(self):
        path = os.path.join(self.__path, 'test.csv')
        adapter.save_info([common.Source(idx='a', type='videoId')], path)
        os.remove(path)

    @mock.patch('ycta_spider.db.build.info_senders')
    def test_send_info(self, _):
        adapter.send_info([], "db::youtube::video_info")