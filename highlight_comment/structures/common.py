__licence__ = 'MIT'
__author__ = 'kuyaki'
__credits__ = ['kuyaki']
__maintainer__ = 'kuyaki'
__date__ = '2022/06/02'

from dataclasses import dataclass
import datetime as dt
from typing import List


@dataclass
class SourceInfo:
    idx: str
    time: dt.datetime


SourceInfoList = List[SourceInfo]
