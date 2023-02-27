"""
Utilities to work with databases.
"""

from enum import Enum
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.sql import select, func
from sqlalchemy.event import listen
from geoalchemy2 import Geometry
from abc import ABC, abstractmethod
from .os_utils import isLinux


class DbType(Enum):
    def __getitem__(self, index):
        return self._value_[index]

    SQLITE_MEM = ["sqlite_mem", "sqlite+pysqlite:///:memory:"]
    SQLITE = ["sqlite", "sqlite://"]
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
        self.name = kwargs.get('name')
        self.type = kwargs.get('type')
        self.is_nullable = kwargs.get('nullable')
        self.default = kwargs.get('default')
        self.is_autoincrement = kwargs.get('autoincrement')
        self.comment = kwargs.get('comment')
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
        self.dynamicLibPath = None
        if isLinux():
            self.dynamicLibPath = '/usr/lib/x86_64-linux-gnu/mod_spatialite.so';

    @abstractmethod
    def getDbInfo(self):
        pass

    def getTables(self, do_order=False, schema=None):
        table_names = self.engine.table_names(schema=schema)
        if do_order:
            table_names = sorted(table_names)
        return table_names
        # engine = create_engine('...')
        # insp = inspect(engine)
        # print(insp.get_table_names())
    
    def getViews(self, do_order=False, schema=None):
        inspector = inspect(self.engine)
        views = inspector.get_view_names()
        if do_order:
            views = sorted(views)
        return views

    def hasView(self, view_name, schema=None):
        views = self.getViews(schema=schema)
        if view_name in views:
            return True
        return False

    def hasTable(self, table_name, schema=None):
        return self.engine.has_table(table_name=table_name, schema=schema)

    def getTableColumns(self, table_name):
        """Get the table columns as list of DbColumn.
        
        :param table_name: the name of the table to get the columns from. 
        :return: the list of DbColumn objects.
        """
        inspector = inspect(self.engine)
        columns = inspector.get_columns(table_name)
        db_cols = [ DbColumn(**item) for item in columns ]
        return db_cols
    
    def getGeometryColumn(self, table_name):
        """Get the geometry columns of a table.
        
        :param table_name: the name of the table to get the geometry column from. 
        :return: the geometry column or None.
        """
        inspector = inspect(self.engine)
        columns = inspector.get_columns(table_name)
        for column in columns:
            dbcolumn = DbColumn(**column)
            if dbcolumn.geoinfo:
                return dbcolumn

    def execute(self, sql_string):
        with self.engine.connect() as conn:
            result = conn.execute(text(sql_string))
            return result
    
    def getTableData(self, table_name, order_by=None, limit=None, where=None):
        """Return the content of a table.

        :param table_name: the table to list data from.
        :param order_by: optional parameter to order the data (name of columns to order by).
        :param limit: optional parameter to limit the return count.
        :param where: optional where clause.
        """
        sql = f"select * from {table_name}"

        if where:
            sql += " where " + where
        if order_by:
            sql += " order by " + order_by
        if limit:
            sql += f" limit {limit}"

        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            return result
    
    def connect(self):
        """
        Get the connection object, if necessary to handle closing manually.
        """
        return self.engine.connect()
    
    def createTable(self, table_object):
        table_object.create(self.engine)
    
    def dropTable(self, table_object):
        table_object.drop(self.engine)
    
    def dropTable(self, table_name, schema=None):
        """Drop a table or view by its name.
        """
        geometry_col = self.getGeometryColumn(table_name)
        with self.engine.connect() as conn:
            trans = conn.begin()

            if self.hasView(table_name, schema=schema):
                result = conn.execute(text(f"drop view if exists {table_name}"))
            elif self.hasTable(table_name, schema=schema):
                if geometry_col:
                    conn.execute(text(f"select DropGeometryColumn('public','{table_name}', '{geometry_col.name}');"))
                result = conn.execute(text(f"drop table if exists {table_name} cascade"))
            trans.commit()
            return result
    
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
    def getDbInfo(self):
        res = self.query(
            "SELECT VERSION() as pgversion, PostGIS_Full_Version() as pgisversion;")
        return [res.pgversion, res.pgisversion]

class SqliteDb(ADb):
    def getDbInfo(self):
        res = self.query(
            "SELECT sqlite_version() as sqliteversion;")
        return [res.pgversion, res.pgisversion]
    

    def initSpatialite(self, dynamicLibPath = None):
        if dynamicLibPath:
            self.dynamicLibPath = dynamicLibPath
        listen(self.engine, 'connect', self.load_spatialite)

        with self.engine.connect() as conn:
            conn.execute(select([func.InitSpatialMetaData()]))

    def load_spatialite(self, dbapi_conn, connection_record):
        dbapi_conn.enable_load_extension(True)
        dbapi_conn.load_extension(self.dynamicLibPath)