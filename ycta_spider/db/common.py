__licence__ = 'MIT'
__author__ = 'pvp'
__credits__ = ['pvp']
__maintainer__ = 'pvp'
__date__ = '2022/07/17'

from abc import abstractmethod
from typing import List, Optional, Any

import psycopg2
from psycopg2.extensions import connection as PsqlConnection

from ycta_spider.file_manager.reader import read_config


class PsqlTable:
    """Use to create and interact with the DB tables.
    Use context syntax, to ensure that no outstanding connections are left hanging."""

    @property
    @abstractmethod
    def _table_creation_query(self) -> str:
        pass

    @property
    @abstractmethod
    def _db(self) -> str:
        pass

    @property
    @abstractmethod
    def _cols(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def _name(self) -> list:
        pass


    def __init__(self, config=None):
        if config is None:
            config = read_config()
        self.__psql_config = config['psql']
        self.__connector = None

    def create_connector(self) -> PsqlConnection:
        return psycopg2.connect(database=self._db, **self.__psql_config)

    def __enter__(self):
        self.__connector = psycopg2.connect(database=self._db, **self.__psql_config)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.__connector.commit()
        self.__connector.close()
        self.__connector = None

    def run_query(self, query: str) -> Optional[List[Any]]:
        """:param query: PostgreSQL query"""
        assert self.__connector is not None, "initialize using with context"
        with self.__connector.cursor() as cur:
            cur.execute(query)
            try:
                return cur.fetchall()
            except psycopg2.ProgrammingError:
                return None
    @classmethod
    def create_table(cls):
        with cls() as conn:
            conn.run_query(conn._table_creation_query)