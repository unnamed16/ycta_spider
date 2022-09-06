from __future__ import annotations

__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/29'

from unittest import TestCase, mock
import json
import requests

from ycta_spider.api.youtube.shell import YoutubeShell
from ycta_spider.structures.common import PlatformType, ResponseCode, Response


class YoutubeShellTestCase(TestCase):
    shell = YoutubeShell()

    def test_constructor(self) -> None:
        self.assertEqual(PlatformType.YOUTUBE, self.shell.platform_type)

    def test_get_channel_id(self) -> None:
        self.assertEqual('UCjWy2g76QZf7QLEwx4cB46g', YoutubeShell.get_channel_id('c/arestovych').content['result'])
        self.assertEqual(ResponseCode.ERROR, YoutubeShell.get_channel_id('fake_infix/channel').code)

    @mock.patch('ycta_spider.api.youtube.shell.YoutubeShell.get_access_token', new=lambda _, auth_code: {'access_token': 'fake'})
    @mock.patch('ycta_spider.api.youtube.shell.save_config')
    def test_access_token(self, mock_save_config):
        self.shell.get_authorization_link()
        self.shell.get_and_write_access_token('')
        self.assertTrue(mock_save_config.called)

    @mock.patch('ycta_spider.api.youtube.shell.requests.get', new=lambda _: Response(code=ResponseCode.ERROR))
    def test_get_comments(self) -> None:
        self.shell.get_comments('Zd1a7qLqqOY')

    @mock.patch('ycta_spider.api.youtube.shell.requests.post')
    def test_add_comments(self, mock_post) -> None:
        self.shell.add_comment('MILSirUni5E', 'test')
        self.assertTrue(mock_post.called)

    @mock.patch('ycta_spider.api.youtube.shell.YoutubeShell._get_video_ids',
                return_value=Response(code=ResponseCode.OK, content={'result': ['']}))
    @mock.patch('ycta_spider.api.youtube.shell.YoutubeShell._get_videos_info',
                return_value=Response(code=ResponseCode.OK, content={'result': ['']}))
    def test_get_sources_info(self, *args) -> None:
        video_ids = ['jZFt9KUvYs8', 'fSNz2tEL5C4', '4n7bUYBYZPE']
        self.assertEqual(self.shell.get_source_info(('videoId', video_ids[0])).code, ResponseCode.OK)
        channel_id = 'UC8zTlrhQ0w1-TZjc2-jdcag'  # https://www.youtube.com/c/AndreAntunesofficial
        self.assertEqual(len(list(self.shell.get_sources_info([
            ('videoId', video_ids[1]),
            ('videoIdList', video_ids[2:]),
            ('channelId', channel_id)
        ], limit=1))), 3)


    def test_get_channels_info(self):
        channel_test_response = requests.models.Response()
        channel_test_response._content = json.dumps({'items': [{'etag': 'etag', 'id': 'id', 'snippet': {
            'title': 'title', 'description': 'desc', 'publishedAt': '2014-02-28T21:48:23Z'
        }}]})
        channel_test_response.status_code = 400
        with mock.patch('ycta_spider.api.youtube.shell.requests.get', return_value=channel_test_response):
            self.shell.get_channels_info(['UCPD_bxCRGpmmeQcbe2kpPaA'])
