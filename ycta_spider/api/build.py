__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/27'

from ycta_spider.api.shell import PlatformType
from ycta_spider.api.vk.shell import Shell as VkShell
from ycta_spider.api.youtube.shell import Shell as YoutubeShell
from ycta_spider.api.telegram.shell import Shell as TelegramShell


def shell(platform_type: PlatformType):
    return {
        PlatformType.VK: VkShell,
        PlatformType.YOUTUBE: YoutubeShell,
        PlatformType.TELEGRAM: TelegramShell,
    }[platform_type]()
