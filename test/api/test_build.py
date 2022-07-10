__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/27'

from unittest import TestCase

from ycta_spider.api.shell import PlatformType
from ycta_spider.api import build


class BuildTestCase(TestCase):

    def test_shell(self) -> None:
        for platform_type in PlatformType:
            shell = build.shell(platform_type)
            self.assertEqual(platform_type, shell.platform_type)
