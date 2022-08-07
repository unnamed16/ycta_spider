__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/29'

from unittest import TestCase, mock

from ycta_spider.api.youtube.shell import Shell
from ycta_spider.structures.common import PlatformType, ResponseCode, Response


class YoutubeShellTestCase(TestCase):

    def test_constructor(self) -> None:
        shell = Shell()
        self.assertEqual(PlatformType.YOUTUBE, shell.platform_type)

    def test_get_channel_id(self) -> None:
        self.assertEqual('UCjWy2g76QZf7QLEwx4cB46g', Shell.get_channel_id('arestovych', 'c').content['result'])
        self.assertEqual(ResponseCode.ERROR, Shell.get_channel_id('NonExistantYoutubeChannel', 'c').code)

    @mock.patch('ycta_spider.api.youtube.shell.Shell.get_access_token', new=lambda _, auth_code: {'access_token': 'fake'})
    @mock.patch('ycta_spider.api.youtube.shell.save_config')
    def test_access_token(self, mock_save_config):
        shell = Shell()
        shell.get_authorization_link()
        shell.get_and_write_access_token('')
        self.assertTrue(mock_save_config.called)

    @mock.patch('ycta_spider.api.youtube.shell.requests.get', new=lambda _: Response(code=ResponseCode.ERROR))
    def test_get_comments(self) -> None:
        shell = Shell()
        shell.get_comments(('videoId', 'Zd1a7qLqqOY'))

    @mock.patch('ycta_spider.api.youtube.shell.requests.post')
    def test_add_comments(self, mock_post) -> None:
        shell = Shell()
        shell.add_comment(('videoId', 'MILSirUni5E'), 'test')
        self.assertTrue(mock_post.called)

    def test_get_source_info(self) -> None:
        # TODO
        shell = Shell()
        channel_id = 'UCBVjMGOIkavEAhyqpxJ73Dw'
        sources_info = list(shell.get_source_info(('channelId', channel_id), limit=10))
        self.assertEqual(10, len(sources_info))
        sources_info = list(shell.get_source_info(('channelId', channel_id), limit=1))
        self.assertEqual(1, len(sources_info))
        sources_info = list(shell.get_source_info(('channelId', channel_id), limit=50))
        self.assertEqual(50, len(sources_info))
        sources_info = list(shell.get_source_info(('channelId', channel_id), limit=100))
        self.assertEqual(100, len(sources_info))
        video_ids = ["MzwD0QlSajk", "zuHjb1lt5QE", "9OuGP9TjTis"]  # the last video should fail to fetch
        sources_info = list(shell.get_sources_info([
            ('videoId', video_ids[2]), ('videoIdList', video_ids)]))
        self.assertEqual(2, len(sources_info))
