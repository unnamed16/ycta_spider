__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/29'

from unittest import TestCase

from highlight_comment.api.youtube.shell import Shell
from highlight_comment.structures.youtube import Channel
from highlight_comment.api.shell import PlatformType, ResponseCode


class YoutubeShellTestCase(TestCase):

    def test_constructor(self) -> None:
        shell = Shell()
        self.assertEqual(PlatformType.YOUTUBE, shell.platform_type)

    def test_get_channel_id(self) -> None:
        self.assertEqual('UCjWy2g76QZf7QLEwx4cB46g', Shell.get_channel_id('arestovych')['result'])
        self.assertEqual(ResponseCode.ERROR, Shell.get_channel_id('NonExistantChannel')['code'])

    def test_get_comments(self) -> None:
        shell = Shell()
        query = shell.get_comments(('videoId', 'Zd1a7qLqqOY'))
        self.assertLessEqual(14, len(list(query)))

    def test_add_comments(self) -> None:
        shell = Shell()
        query = shell.add_comment('videoId=MILSirUni5E', 'test')
        self.assertEqual(ResponseCode.OK, query['code'])
        self.assertIn('result', query)

    def test_get_video_ids(self) -> None:
        shell = Shell()
        channel_id = 'UCBVjMGOIkavEAhyqpxJ73Dw'
        query = shell.get_video_ids(Channel(channelId=channel_id))
        self.assertEqual(ResponseCode.OK, query['code'])
        self.assertIn('result', query)
