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
    columns = None
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
        'List[str]': lambda l: '\'{"' + '", "'.join(l) + '"}\''
    }

    def to_query_vals(self) -> str:
        return '(' + ', '.join([
            self.__psql_mapper[t](self.__dict__[c])
            for c, t in zip(self.columns, self._types)
        ]) + ')'

    @classmethod
    def build(cls):
        """run once for each class you'd want to instantiate"""
        cls.columns = []
        cls._types = []
        for f in fields(cls):
            cls.columns.append(f.name)
            cls._types.append(f.type)

    @classmethod
    def inst_from_psql_output(cls, vals: List) -> PsqlEntry:
        """create object from the output of an sql query"""
        return cls(**dict(zip(cls.columns, vals)))  # noqa: F401


@dklass_kwonly
class TimedEntry(PsqlEntry):
    idx: str
    time: dt.datetime = field(default_factory=lambda: dt.datetime.now())

@dklass_kwonly
class GradedEntry(TimedEntry):
    grade: float = 0.
    grade_confidence: float = 0.

@dklass_kwonly
class Source(GradedEntry):
    type: str = ''
    title: str = ''


Source.build()
Sources = Iterable[Source]


@dklass_kwonly
class Comment(GradedEntry):
    text: str
    access_count: int = 0


Comment.build()
Comments = Iterable[Comment]

Info = Union[Sources, Comments]
