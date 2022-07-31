__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/27'

from ycta_spider.structures.common import PlatformType
from ycta_spider.api.youtube.shell import Shell as YoutubeShell

__shells = {
    PlatformType.YOUTUBE: YoutubeShell
}

def shell(platform_type: PlatformType):
    return __shells[platform_type]()