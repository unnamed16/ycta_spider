__license__ = 'MIT'
__author__ = 'pvp'
__maintainer__ = 'pvp'
__date__ = '7/30/2022'

from ycta_spider.db.youtube import send_info as youtube_send_info

info_senders = {
    'youtube': youtube_send_info
}