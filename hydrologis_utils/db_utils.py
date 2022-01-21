"""
Utilities to work with databases.
"""

from enum import Enum
from sqlalchemy import create_engine, text, inspect
from geoalchemy2 import Geometry, Geography
from abc import ABC, abstractmethod


class DbType(Enum):
    def __getitem__(self, index):
        return self._value_[index]

    SQLITE_MEM = ["sqlite_mem", "sqlite+pysqlite:///:memory:"]
    POSTGRESQL = ["postgres", "postgresql+psycopg2://"] # needs psycopg2 available

    def label(self):
        return self[0]

    def dialect(self):
        return self[1]

    def url(self, dbname=None, host=None, port=None, user=None, pwd=None):
        urlString = self[1]
        if user and pwd:
            urlString += f"{user}:{pwd}@"
        if host:
            urlString += host
        if port:
            urlString += f":{port}"
        if dbname:
            urlString += f"/{dbname}"
        return urlString

class DbColumn:
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.type = kwargs['type']
        self.is_nullable = kwargs['nullable']
        self.default = kwargs['default']
        self.is_autoincrement = kwargs['autoincrement']
        self.comment = kwargs['comment']
        self.geoinfo = None
        if isinstance(self.type, Geometry):
            self.geoinfo = GeoInfo(self.type)

    def __str__(self):
        s = f"{self.name} "
        if self.geoinfo:
            s += f"({self.geoinfo})"
        else:
            s += f"({self.type})"
        return s

class GeoInfo:
    def __init__(self, geom_type):
        self.name = geom_type.name
        self.type = geom_type.geometry_type
        self.srid = geom_type.srid
        self.dimension = geom_type.dimension
        self.has_index = geom_type.spatial_index

    def __str__(self):
        return f"{self.type}, {self.srid}, DIM={self.dimension}, IDX={self.has_index}"
    

class ADb(ABC):
    def __init__(self, url, encoding="utf-8", echo=True, future=False):
        self.url = url
        self.engine = create_engine(
            url, echo=echo, future=future, encoding=encoding)

    @abstractmethod
    def get_db_info(self):
        pass

    def get_tables(self, do_order=False, schema='public'):
        table_names = self.engine.table_names(schema=schema)
        if do_order:
            table_names = sorted(table_names)
        return table_names
        # engine = create_engine('...')
        # insp = inspect(engine)
        # print(insp.get_table_names())

    def has_table(self, table_name, schema=None):
        return self.engine.has_table(table_name=table_name, schema=schema)

    def get_table_columns(self, table_name):
        """Get the table columns as list of DbColumn.
        
        :param table_name: the name of the table to get the columns from. 
        :return: the list of DbColumn objects.
        """
        inspector = inspect(self.engine)
        columns = inspector.get_columns(table_name)
        db_cols = [ DbColumn(**item) for item in columns ]
        return db_cols

    def query(self, sql_string):
        with self.engine.connect() as conn:
            result = conn.execute(text(sql_string))
            return result
    
    def get_table(self, table_name):
        """Return the content of a table.
        """
        with self.engine.connect() as conn:
            result = conn.execute(text(f"select * from {table_name}"))
            return result
    
    def create_table(self, table_object):
        table_object.create(self.engine)
    
    def drop_table(self, table_object):
        table_object.drop(self.engine)
    
    def insert(self, table_object, data_list):
        with self.engine.connect() as conn:
            result = conn.execute(table_object.insert(), data_list)
            return result
    
    def select(self, select_object):
        with self.engine.connect() as conn:
            result = conn.execute(select_object)
            return result
    
    def decode(self, obj):
        """Decode values to their scalar or string representation.

        :param obj: the object to convert.
        :return: the decoded object.
        """
        with self.engine.connect() as conn:
            return conn.scalar(obj)

class PostgresDb(ADb):
    def get_db_info(self):
        res = self.query(
            "SELECT VERSION() as pgversion, PostGIS_Full_Version() as pgisversion;")
        return [res.pgversion, res.pgisversion]
