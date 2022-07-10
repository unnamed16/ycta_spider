__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/29'

from unittest import TestCase

from ycta_spider.api.telegram.shell import Shell
from ycta_spider.api.shell import PlatformType


class KucoinShellTestCase(TestCase):

    def test_constructor(self) -> None:
        shell = Shell()
        self.assertEqual(PlatformType.TELEGRAM, shell.platform_type)
