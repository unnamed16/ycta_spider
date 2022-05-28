__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/29'

from unittest import TestCase

from highlight_comment.api.vk.shell import Shell
from highlight_comment.api.shell import PlatformType


class BinanceShellTestCase(TestCase):

    def test_constructor(self) -> None:
        shell = Shell()
        self.assertEqual(PlatformType.VK, shell.platform_type)
