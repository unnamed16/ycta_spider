__licence__ = 'MIT'
__author__ = 'pvp'
__credits__ = ['pvp']
__maintainer__ = 'pvp'
__date__ = '2022/07/17'

from abc import abstractmethod

import psycopg2

from ycta_spider.file_manager.reader import read_config


class PsqlConnector:
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
    def _cols(self) -> list:
        pass

    def __init__(self, config=None):
        if config is None:
            config = read_config()
        self._psql_config = config['psql']
        self._connector = None

    def __enter__(self):
        self._connector = psycopg2.connect(database=self._db, **self._psql_config)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._connector.commit()
        self._connector.close()
        self._connector = None

    def run_query(self, query: str):
        """:param query: PostgreSQL query"""
        assert self._connector is not None, "initialize using with context"
        with self._connector.cursor() as cur:
            cur.execute(query)

    def _create_table(self):
        self.run_query(self._table_creation_query)