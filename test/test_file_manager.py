__license__ = 'MIT'
__author__ = 'ppv'
__maintainer__ = 'ppv'
__date__ = '8/6/2022'

from unittest import TestCase, mock

from ycta_spider.file_manager.reader import read_config, CONFIG_PATH
from ycta_spider.file_manager.writer import save_config


class TestFileManager(TestCase):

    def test_read_config(self):
        try:
            read_config()
        except Exception as e:
            print(e)
            print('(did you forget to turn config.template.json into config.json and fill out the required fields?)')
            return

    @mock.patch('ycta_spider.file_manager.writer.__CONFIG_LOCK')
    @mock.patch('ycta_spider.file_manager.writer.json.dumps')
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_read_write_config(self, mock_fastener, mock_dumps, _) -> None:
        save_config(dict())
        self.assertTrue(mock_fastener.called)
        self.assertTrue(mock_dumps.called)

