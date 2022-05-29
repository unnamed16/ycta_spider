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

    def test_get_channel_id(self) -> None:
        self.assertEquals('UCjWy2g76QZf7QLEwx4cB46g', Shell.get_channel_id('arestovych')['result'])
        self.assertEquals(ResponseCode.ERROR, Shell.get_channel_id('NonExistantChannel')['code'])

    def test_get_comments(self) -> None:
        shell = Shell()
        query = shell.get_comments('videoId=Zd1a7qLqqOY')
        self.assertEqual(ResponseCode.OK, query['code'])
        self.assertIn('result', query)
        self.assertLessEqual(4, len(query['result']))

    def test_add_comments(self) -> None:
        shell = Shell()
        query = shell.add_comment('videoId=MILSirUni5E', 'test')
        self.assertEqual(ResponseCode.OK, query['code'])
        self.assertIn('result', query)

    def test_get_video_ids(self) -> None:
        shell = Shell()
        channel_id = 'UCBVjMGOIkavEAhyqpxJ73Dw'
        max_results = 10
        order = shell.SearchOrder.DATE
        query = shell.get_video_ids(channel_id, max_results, order)
        self.assertEqual(ResponseCode.OK, query['code'])
        self.assertIn('result', query)