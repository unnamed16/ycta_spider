__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/29'

from unittest import TestCase

from highlight_comment.api.youtube.shell import Shell
from highlight_comment.api.shell import PlatformType, ResponseCode


class YoutubeShellTestCase(TestCase):

    def test_constructor(self) -> None:
        shell = Shell()
        self.assertEqual(PlatformType.YOUTUBE, shell.platform_type)

    def test_channel_id(self) -> None:
        self.assertEquals('UCjWy2g76QZf7QLEwx4cB46g', Shell.get_channel_id('arestovych')['result'])
        self.assertEquals(ResponseCode.ERROR, Shell.get_channel_id('NonExistantChannel')['code'])