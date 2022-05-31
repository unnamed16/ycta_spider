__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/29'

from unittest import TestCase


class YoutubeDataTestCase(TestCase):
    from highlight_comment.data import youtube

    def test_load_channels(self) -> None:
        channels = self.youtube.ChannelCache.load_channels()
        self.assertEqual('DmitryPuchkov', channels[0].name)