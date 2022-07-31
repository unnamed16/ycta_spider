__license__ = 'MIT'
__author__ = 'ppv'
__maintainer__ = 'ppv'
__date__ = '7/31/2022'

import unittest
import datetime as dt

from ycta_spider.structures import common


class CommonStructuresTestCase(unittest.TestCase):

    def test_source(self):
        source = common.Source(idx='idx', grade_confidence=-1, title='some', time=dt.datetime(1966, 6, 6, 6, 6))
        self.assertEqual(source._cols, ['idx', 'time', 'grade', 'grade_confidence', 'title'])
        self.assertEqual(source.to_query_vals(), "('idx', '1966-06-06 06:06:00', 0.0, -1, 'some')")
        self.assertEqual(source, common.Source.inst_from_psql_output([
            source.idx, source.time, source.grade, source.grade_confidence, source.title
        ]))


    def test_comment(self):
        comment = common.Comment(idx='idx', text='some', access_count=10)
        self.assertEqual(comment._cols, ['idx', 'time', 'grade', 'grade_confidence', 'text', 'access_count'])
        self.assertEqual(comment.to_query_vals(), f"('idx', '{comment.time}', 0.0, 0.0, 'some', 10)")
        self.assertEqual(comment, common.Comment.inst_from_psql_output([
            comment.idx, comment.time, comment.grade, comment.grade_confidence, comment.text, comment.access_count
        ]))