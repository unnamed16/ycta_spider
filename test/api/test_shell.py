__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/29'

from unittest import TestCase

from ycta_spider.api.shell import PlatformType
from ycta_spider.api import build


class CommonShellTestCase(TestCase):

    def test_get_comments(self) -> None:
        for platform_type in PlatformType:
            print(f'\r{platform_type}', end='')
            shell = build.shell(platform_type)
            self.assertEqual(platform_type, shell.platform_type)
        print('\r', end='')

    def test_add_comment(self) -> None:
        for platform_type in PlatformType:
            print(f'\r{platform_type}', end='')
            shell = build.shell(platform_type)
            self.assertEqual(platform_type, shell.platform_type)
        print('\r', end='')
