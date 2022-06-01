__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/30'

from unittest import TestCase

from highlight_comment.file_manager.reader import read_config


class ReaderTestCase(TestCase):

    def test_read_config(self) -> None:
        cfg = read_config()
        self.assertIn("platforms", cfg)
        self.assertIn("sources", cfg)
        self.assertIn("responses", cfg)
        self.assertEqual(5, len(cfg))

    def test_read_json(self) -> None:
        pass

    def test_read_file(self) -> None:
        pass

    def test_read_files(self) -> None:
        pass

    def test_browse_file_sub_paths(self) -> None:
        pass
