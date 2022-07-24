from __future__ import annotations

__licence__ = 'MIT'
__author__ = 'pvp'
__credits__ = ['pvp']
__maintainer__ = 'pvp'
__date__ = '2022/06/02'

from dataclasses import dataclass
import datetime as dt
from typing import List


@dataclass
class SourceInfo:
    idx: str
    time: dt.datetime

    @classmethod
    def psql_cols(cls) -> List:
        return ['idx', 'time'] + list(cls.__annotations__.keys())

    @classmethod
    def psql_from_value(cls, cols: List, vals: List) -> SourceInfo:
        return cls(**dict(zip(cols, vals)))

    def psql_to_value(self, cols: List) -> str:
        values = [f"'{field}'" for field in [self.idx, self.time]]
        for c in cols[2:]:
            tp = self.__annotations__[c]
            value = self.__dict__[c]
            if tp == str or tp == dt.datetime:
                values.append(f"'{value}'")
            elif tp == int:
                values.append(str(value))
            elif tp == List[str]:
                values.append("'{\"" + '","'.join(value) + "\"}'")
            else:
                raise NotImplementedError(f'type {tp} not supported by SourceInfo')
        return '(' + ', '.join(values) + ')'


SourceInfoList = List[SourceInfo]
