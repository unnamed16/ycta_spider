__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/29'

from unittest import TestCase

import ycta_spider.db.youtube


class YoutubeDataTestCase(TestCase):

    def test_load_channels(self) -> None:
        channels = ycta_spider.db.youtube.ChannelCache.load_channels()
        self.assertEqual('DmitryPuchkov', channels[0].name)
