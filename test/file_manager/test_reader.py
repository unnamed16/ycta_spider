__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/30'

from unittest import TestCase

from ycta_spider.file_manager.reader import read_config


class ReaderTestCase(TestCase):

    def test_config(self) -> None:
        cfg = read_config()
        self.assertIn("platforms", cfg)
        self.assertIn("sources", cfg)
        self.assertIn("responses", cfg)
        self.assertIn("psql", cfg)
