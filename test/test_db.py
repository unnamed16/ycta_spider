__licence__ = 'MIT'
__author__ = 'pvp'
__credits__ = ['pvp']
__maintainer__ = 'pvp'
__date__ = '2022/07/17'

from unittest import TestCase

from ycta_spider.adapter import send_info
from ycta_spider.api.youtube.shell import Shell


class YoutubeDbTestCase(TestCase):

    def test_send_video_info(self):
        shell = Shell()
        test_video_ids = ["bGbziRU11TA", "zN0SjH2_79s"]
        video_info_iterator = shell.get_sources_info([('videoId', id) for id in test_video_ids])
        send_info(video_info_iterator, 'youtube', 'video_info')
