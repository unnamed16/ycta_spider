__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/29'

from unittest import TestCase

from highlight_comment.api.shell import ResponseCode, PlatformType, Comment
from highlight_comment.api import build


class CommonShellTestCase(TestCase):

    def test_get_comments(self) -> None:
        for platform_type in PlatformType:
            if platform_type is not PlatformType.YOUTUBE:
                continue
            print(f'\r{platform_type}', end='')
            shell = build.shell(platform_type)
            query = shell.get_comments('videoId=Zd1a7qLqqOY')
            self.assertEqual(ResponseCode.OK, query['code'])
            self.assertIn('result', query)
            for comment in query['result']:
                self.assertEqual(Comment, type(comment))
        print('\r', end='')

    def test_add_comment(self) -> None:
        for platform_type in PlatformType:
            if platform_type is not PlatformType.YOUTUBE:
                continue
            print(f'\r{platform_type}', end='')
            shell = build.shell(platform_type)
            query = shell.add_comment('videoId=Zd1a7qLqqOY', 'Ааааха ресурс )))')
            self.assertEqual(ResponseCode.OK, query['code'])
            self.assertIn('result', query)
            for comment in query['result']:
                self.assertEqual(Comment, type(comment))
        print('\r', end='')
