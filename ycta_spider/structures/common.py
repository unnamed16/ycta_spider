from __future__ import annotations

__licence__ = 'MIT'
__author__ = 'pvp'
__credits__ = ['pvp']
__maintainer__ = 'pvp'
__date__ = '2022/06/02'

from dataclasses import dataclass, fields, field
import datetime as dt
from enum import Enum
from typing import List, Any, Dict, Iterable, Tuple


class PlatformType(Enum):
    YOUTUBE = 'YOUTUBE'


class ResponseCode(Enum):
    OK = 'OK'
    ERROR = 'ERROR'
    PARSE_ERROR = 'PARSE ERROR'
    UNKNOWN = 'UNKNOWN'
    TOO_FREQUENT = 'TOO FREQUENT'


@dataclass
class Response:
    code: ResponseCode
    content: Dict[str, Any] = field(default_factory=lambda: dict())


@dataclass(kw_only=True)
class PsqlEntry:
    _cols = None
    _types = None
    _not_built = True  # to avoid building twice

    __add_quotes = lambda value: f"'{value}'"
    __psql_mapper = {
        'str': __add_quotes,
        'dt.datetime': __add_quotes,
        'int': str,
        'float': str
    }

    def to_query_vals(self) -> str:
        return '(' + ', '.join([
            self.__psql_mapper[t](self.__dict__[c])
            for c, t in zip(self._cols, self._types)
        ]) + ')'

    @classmethod
    def build(cls):
        """run once for each class you'd want to instantiate"""
        # an alternative is "lazy property" involving _cols and _types,
        # but that introduces a bunch of annoying conditionals
        assert cls._not_built
        cls._cols = []
        cls._types = []
        for f in fields(cls):
            cls._cols.append(f.name)
            cls._types.append(f.type)
        cls._not_built = False

    @classmethod
    def inst_from_psql_output(cls, vals: List) -> PsqlEntry:
        """create object from the output of an sql query"""
        return cls(**dict(zip(cls._cols, vals)))  # noqa: F401


@dataclass(kw_only=True)
class TimedEntry(PsqlEntry):
    idx: str
    time: dt.datetime = field(default_factory=lambda: dt.datetime.now())


@dataclass
class GradedEntry(TimedEntry):
    grade: float = 0.
    grade_confidence: float = 0.


@dataclass(kw_only=True)
class Source(GradedEntry):
    type: str = ''  # e.g., videoId
    title: str = ''  # aka human-readable ID

    def as_tuple(self) -> Tuple[str, str]:
        return self.type, self.idx

    @classmethod
    def from_tuple(cls, tp: Tuple[str, str]) -> Source:
        t, idx = tp
        return cls(idx=idx, type=t)


Source.build()


@dataclass(kw_only=True)
class Comment(GradedEntry):
    text: str = ''
    access_count: int = 0


Comment.build()

Comments = Iterable[Comment]
