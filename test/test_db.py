__licence__ = 'MIT'
__author__ = 'pvp'
__credits__ = ['pvp']
__maintainer__ = 'pvp'
__date__ = '2022/07/17'

from unittest import TestCase

from ycta_spider.adapter import send_info
from ycta_spider.api.youtube.shell import YoutubeShell
from ycta_spider.db import youtube as youtube_db


class YoutubeDbTestCase(TestCase):

    def test_send_info(self):
        shell = YoutubeShell()
        test_video_ids = ["bGbziRU11TA", "zN0SjH2_79s"]
        video_info = list(shell.get_sources_info([('videoId', idx) for idx in test_video_ids]))
        send_info(video_info, 'db::youtube::video_info')
        recovered_video_info = youtube_db.YoutubeVideoTable.get_info_by_idxs(test_video_ids[:1]).content['result'][0]
        self.assertEqual(recovered_video_info, video_info[0])

        primary_comments = []
        secondary_comments = []
        for pc, scs in shell.get_comments(test_video_ids[0], limit=1):
            primary_comments.append(pc)
            secondary_comments += scs
        send_info(primary_comments, 'db::youtube::primary_comments')
        send_info(secondary_comments, 'db::youtube::secondary_comments')
        recovered_primary_comment = youtube_db.YoutubePrimaryCommentTable.get_info_by_idxs([primary_comments[0].idx]).content['result'][0]
        self.assertEqual(recovered_primary_comment, primary_comments[0])
        recovered_secondary_comment = youtube_db.YoutubeSecondaryCommentTable.get_info_by_idxs([secondary_comments[0].idx]).content['result'][0]
        self.assertEqual(recovered_secondary_comment, secondary_comments[0])

        channel_id = recovered_video_info.channel_id
        channels_info = shell.get_channels_info([channel_id]).content['result']
        send_info(channels_info, 'db::youtube::channel_info')
        recovered_channels_info = youtube_db.YoutubeChannelTable.get_info_by_idxs([channels_info[0].idx]).content['result'][0]
        self.assertEqual(recovered_channels_info, channels_info[0])
