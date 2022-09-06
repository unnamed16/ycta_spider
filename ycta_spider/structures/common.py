from __future__ import annotations

__licence__ = 'MIT'
__author__ = 'pvp'
__credits__ = ['pvp']
__maintainer__ = 'pvp'
__date__ = '2022/06/02'

from dataclasses import dataclass, fields, field
import datetime as dt
from enum import Enum
from functools import partial
from typing import List, Any, Dict, Iterable, Union

import pytz

dklass_kwonly = partial(dataclass, kw_only=True)

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

Responses = Iterable[Response]


@dataclass
class PsqlEntry:
    _columns = None
    _types = None

    def __str__(self):
        return "\n".join(["\t" + c.ljust(20) + str(self.__dict__[c]) for c in self.columns])

    __add_quotes_replace_single_quote = lambda s: "'" + s.replace("'", "''") + "'"
    __add_quotes = lambda v: f"'{v}'"
    __psql_mapper = {
        'str': __add_quotes_replace_single_quote,
        'dt.datetime': __add_quotes,
        'int': str,
        'float': str,
        'List[str]': lambda l: '\'{"' + ('", "'.join(l)).replace("'", "''") + '"}\''
    }

    def to_query_vals(self) -> str:
        return '(' + ', '.join([
            self.__psql_mapper[t](self.__dict__[c])
            for c, t in zip(self.columns, self._types)
        ]) + ')'

    @classmethod
    @property
    def columns(self) -> List[str]:
        """run once for each class you'd want to instantiate"""
        if self._columns is None:
            self._columns = []
            self._types = []
            for f in fields(self):
                self._columns.append(f.name)
                self._types.append(f.type)
        return self._columns

    @classmethod
    def inst_from_psql_output(cls, vals: List) -> PsqlEntry:
        """create object from the output of an sql query"""
        return cls(**dict(zip(cls.columns, vals)))  # noqa


@dklass_kwonly
class TimedEntry(PsqlEntry):
    idx: str
    time: dt.datetime = field(default_factory=lambda: dt.datetime.now(pytz.utc))

@dklass_kwonly
class GradedEntry(TimedEntry):
    grade: float = 0.
    grade_confidence: float = 0.
    access_count: int = 0

@dklass_kwonly
class Source(GradedEntry):
    pass


Sources = Iterable[Source]


@dklass_kwonly
class Comment(GradedEntry):
    text: str


Comments = Iterable[Comment]

Info = Union[Sources, Comments]
