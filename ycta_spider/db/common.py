__licence__ = 'MIT'
__author__ = 'pvp'
__credits__ = ['pvp']
__maintainer__ = 'pvp'
__date__ = '2022/07/17'

from abc import abstractmethod
from typing import List, Optional, Any

import psycopg2
from psycopg2.extensions import connection as PsqlConnection
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

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

    _psql_config = read_config()['psql']
    _db_creation_verified = False
    _table_creation_verified = False

    @classmethod
    def _verify_table_creation(cls):
        if cls._table_creation_verified:
            return
        with psycopg2.connect(database=cls._db, **cls._psql_config) as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_catalog='{cls._db}' AND table_schema='public' AND table_name='{cls._name}');")
                conn.commit()
                table_exists = cur.fetchall()[0][0]
        cls._table_creation_verified = True
        if not table_exists:
            cls.create_table()
    @classmethod
    def _verify_db_creation(cls):
        if cls._db_creation_verified:
            return
        try:
            psycopg2.connect(database=cls._db, **cls._psql_config).close()
        except psycopg2.OperationalError:
            with psycopg2.connect(**cls()._psql_config) as conn:
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                with conn.cursor() as cur:
                    cur.execute(f'create database "{cls._db}"')
        cls._db_creation_verified = True


    def __init__(self, config=None):
        if config is not None:
            self._psql_config = config['psql']
        self.__connector = None
        self._verify_db_creation()
        self._verify_table_creation()


    def create_connector(self) -> PsqlConnection:
        return psycopg2.connect(database=self._db, **self._psql_config)

    def __enter__(self):
        self.__connector = psycopg2.connect(database=self._db, **self._psql_config)
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