__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/05/27'

from highlight_comment.api.shell import PlatformType
from highlight_comment.api.vk.shell import Shell as VkShell
from highlight_comment.api.youtube.shell import Shell as YoutubeShell
from highlight_comment.api.telegram.shell import Shell as TelegramShell


def shell(platform_type: PlatformType):
    return {
        PlatformType.VK: VkShell,
        PlatformType.YOUTUBE: YoutubeShell,
        PlatformType.TELEGRAM: TelegramShell,
    }[platform_type]()
