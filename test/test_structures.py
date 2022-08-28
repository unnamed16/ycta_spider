__license__ = 'MIT'
__author__ = 'ppv'
__maintainer__ = 'ppv'
__date__ = '7/31/2022'

import unittest
import datetime as dt

from ycta_spider.structures import common
from ycta_spider.structures.youtube import process_top_level_comments


class CommonStructuresTestCase(unittest.TestCase):

    def test_comment(self):
        comment = common.Comment(idx='idx', text='some', access_count=10)
        self.assertEqual(comment.columns, ['idx', 'time', 'grade', 'grade_confidence', 'access_count', 'text'])
        self.assertEqual(comment.to_query_vals(), f"('idx', '{comment.time}', 0.0, 0.0, 10, 'some')")
        self.assertEqual(comment, common.Comment.inst_from_psql_output([
            comment.idx, comment.time, comment.grade, comment.grade_confidence, comment.access_count, comment.text]))


class YoutubeStructuresTestCase(unittest.TestCase):

    def test_process_top_level_comments(self):
        primary_comment, secondary_comments = process_top_level_comments({
            'etag': 'TizpY-Ka6etskkDlr8dBdDnqEAY',
            'id': 'UgylaJIYN8uR9AL4Qnp4AaABAg',
            'snippet': {
                'videoId': 'J1tWas5xe0s',
                'topLevelComment': {
                    'etag': 'jfpQyYiww9199gRPE44l--b25SY',
                    'id': 'UgylaJIYN8uR9AL4Qnp4AaABAg',
                    'snippet': {
                        'videoId': 'J1tWas5xe0s',
                        'textDisplay': 'some_text',
                        'textOriginal': 'some_text',
                        'authorDisplayName': 'Олександра',
                        'authorChannelId': {'value': 'UC6kGiwKkD8a1NXTgj8l24vQ'},
                        'likeCount': 72,
                        'publishedAt': '2022-08-20T14:42:43Z',
                        'updatedAt': '2022-08-20T14:42:43Z'}
                }, 'totalReplyCount': 4},
            'replies': {'comments': [{
                'kind': 'youtube#comment',
                'etag': 'RqFpYpTez4RxUtxeawhXwoK_9Bc',
                'id': 'UgylaJIYN8uR9AL4Qnp4AaABAg.9exYhZXlAo89f-1f9pgXR1',
                'snippet': {
                    'videoId': 'J1tWas5xe0s',
                    'textDisplay': 'someText',
                    'textOriginal': 'SomeText',
                    'authorDisplayName': 'Tatiana Serguienko',
                    'authorChannelId': {'value': 'UC3SKPAzHeCV-AeYrijS0DOQ'},
                    'likeCount': 0,
                    'publishedAt': '2022-08-21T13:51:45Z',
                    'updatedAt': '2022-08-21T13:51:45Z'}}]}
        })
        self.assertEqual(secondary_comments[0].parent_idx, primary_comment.idx)