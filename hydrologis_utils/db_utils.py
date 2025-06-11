"""
Utilities to work with databases.
"""

from enum import Enum
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.sql import select, func
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.event import listen
from geoalchemy2 import Geometry
from abc import ABC, abstractmethod
from .os_utils import isLinux, isWindows, isMacos
from geoalchemy2 import load_spatialite_gpkg, load_spatialite
from sqlalchemy.event import listen
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
import os

import logging
logger = logging.getLogger(__name__)

class DbType(Enum):
    def __getitem__(self, index):
        return self._value_[index]

    SQLITE_MEM = ["sqlite_mem", "sqlite+pysqlite:///:memory:"]
    SQLITE = ["sqlite", "sqlite://"]
    SPATIALITE = ["spatialite", "sqlite://"]
    GPKG = ["gpkg", "gpkg://"]
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
    def __init__(self, url, encoding=None, echo=True):
        self.supportsSchema = True
        self.url = url
        if encoding:
            self.engine = create_engine(
                f"{url}?charset={encoding}", echo=echo)
        else:
            self.engine = create_engine(
                url, echo=echo)
        self.dynamicLibPath = None
        self.metadata = MetaData()
        # self.metadata.reflect(bind=self.engine)



    @abstractmethod
    def getDbInfo(self):
        pass

    def getTables(self, do_order=False, schema=None) -> list[str]:
        inspector = inspect(self.engine)
        table_names = inspector.get_table_names(schema=schema)

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

    def hasView(self, view_name, schema=None) -> bool:
        views = self.getViews(schema=schema)
        if view_name in views:
            return True
        return False

    def hasTable(self, table_name, schema=None) -> bool:
        inspector = inspect(self.engine)
        return inspector.has_table(table_name, schema=schema)

    def getTableColumns(self, table_name) -> list[DbColumn]:
        """Get the table columns as list of DbColumn.
        
        :param table_name: the name of the table to get the columns from. 
        :return: the list of DbColumn objects.
        """
        inspector = inspect(self.engine)
        columns = inspector.get_columns(table_name)
        db_cols = [ DbColumn(**item) for item in columns ]
        return db_cols
    
    def getGeometryColumn(self, table_name) -> DbColumn:
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
        """Execute a sql statement.

        :param sql_string: the sql statement to execute.
        """
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

        # Replace 'your_table_name' with the actual name of your table
        table = Table(table_name, self.metadata, autoload_with=self.engine)

        stmt = select(table)
        if where:
            stmt = stmt.where(text(where))
        if order_by:
            stmt = stmt.order_by(text(order_by))
        if limit:
            stmt = stmt.limit(limit)

        with self.engine.connect() as conn:
            result = conn.execute(stmt)
            return result.all()


        # cols = self.getTableColumns(table_name)
        # cols = [c.name for c in cols]
        # sql = f"select {','.join(cols)} from {table_name}"

        # if where:
        #     sql += " where " + where
        # if order_by:
        #     sql += " order by " + order_by
        # if limit:
        #     sql += f" limit {limit}"

        # dataList = []
        # with self.engine.connect() as conn:
        #     result = conn.execute(text(sql))

        #     for row in result:
        #         i = 0
        #         item = {}
        #         for col in cols:
        #             item[col] = row[i]
        #             i=i+1
        #         dataList.append(item)
                
        # return dataList
    
    def getRecordCount(self, table_name) -> int:
        """Return the count of the records of a table.

        :param table_name: the table to list data from.
        """
        sql = f"select count(*) from {table_name}"

        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            return result.first()[0]
    
    def connect(self):
        """
        Get the connection object, if necessary to handle closing manually.
        """
        return self.engine.connect()
    
    def createTable(self, table_object) -> None:
        table_object.create(self.engine)
    
    def dropTable(self, table_object) -> None:
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
    
    def insertOrmWithParams(self, table_object, data):
        """
        Execute an insert statement with parameters in single or bulk mode.

        :param table_object: the table object to insert into.
        :param data: the data to insert. Can be a dict of data or a list of dicts for bulk mode.
        """
        with Session(self.engine) as session:
            insertStmt = table_object.insert().values(data)
            result = session.execute(insertStmt)
            session.commit()
            return result.rowcount


    def insertSqlWithParams(self, sql_string, data):
        """Execute an insert sql statement with parameters in single or bulk mode.

        Make sure to use proper substitutions:

            INSERT INTO table (id, value) VALUES (:id, :value)

        with dicts:
            
            [{"id":1, "value":"v1"}, {"id":2, "value":"v2"}]
            

        :param sql_string: the sql statement to execute.
        :param data: the data to insert. Can be a dict of data or a list of dicts for bulk mode.
        """

        with Session(self.engine) as session:
            result = session.execute(text(sql_string), data)
            session.commit()
            return result.rowcount
    
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

    # init class calling super
    def __init__(self, url, encoding="utf-8", echo=True):
        super().__init__(url, encoding=encoding, echo=echo)
        self.supportsSchema = False

    def getDbInfo(self):
        res = self.query(
            "SELECT sqlite_version() as sqliteversion;")
        return [res.pgversion, res.pgisversion]
    
def _checkSpatialiteLibraryPath(dynamicLibPath):
    libspath = os.environ.get('SPATIALITE_LIBRARY_PATH')
    if not libspath:
        if isLinux():
            if not dynamicLibPath:
                dynamicLibPath = '/usr/lib/x86_64-linux-gnu/mod_spatialite.so';
        elif isWindows():
            if not dynamicLibPath:
                dynamicLibPath = 'C:/Program Files/SpatiaLite/mod_spatialite.dll';
        elif isMacos():
            if not dynamicLibPath:
                dynamicLibPath = '/usr/local/lib/mod_spatialite.dylib';
        os.environ['SPATIALITE_LIBRARY_PATH'] = dynamicLibPath
        logger.warning(f"SPATIALITE_LIBRARY_PATH not set, trying to set it automatically to {os.environ['SPATIALITE_LIBRARY_PATH']}.")


class GpkgDb(ADb):
    TABLE_TILES = "tiles";
    COL_TILES_ZOOM_LEVEL = "zoom_level";
    COL_TILES_TILE_COLUMN = "tile_column";
    COL_TILES_TILE_ROW = "tile_row";
    COL_TILES_TILE_DATA = "tile_data";
    SELECTQUERY = "SELECT tile_data from {} where zoom_level={} AND tile_column={} AND tile_row={}"
    

    def __init__(self, url, encoding="utf-8", echo=True):
        super().__init__(url, encoding=encoding, echo=echo)
        self.supportsSchema = False
        _checkSpatialiteLibraryPath(self.dynamicLibPath)
        listen(self.engine, "connect", load_spatialite_gpkg)
        self.tileRowType = "osm"; # could be tms in some cases

    def getDbInfo(self):
        res = self.query(
            "SELECT sqlite_version() as sqliteversion;")
        return [res.pgversion, res.pgisversion]
    
    def getTile(self, tableName:str, tx:int, tyOsm:int, zoom:int):
        ty = tyOsm;
        if self.tileRowType == "tms":
            tmsTileXY = self.osmTile2TmsTile(tx, tyOsm, zoom)
            ty = tmsTileXY[1]

        sql = GpkgDb.SELECTQUERY.format(tableName,zoom, tx, ty)
        result = self.execute(sql)
        for row in result:
            if row[0]:
                return row[0]
        return None
    
    
    def osmTile2TmsTile(self, tx:int, ty:int, zoom:int):
        return [tx, int((pow(2, zoom) - 1) - ty)];
    

class SpatialiteDb(ADb):
    def __init__(self, url, encoding="utf-8", echo=True, dynamicLibPath=None):
        super().__init__(url, encoding=encoding, echo=echo)
        self.dynamicLibPath = dynamicLibPath
        self.supportsSchema = False
        _checkSpatialiteLibraryPath(self.dynamicLibPath)
        listen(self.engine, 'connect', load_spatialite)

    def getDbInfo(self):
        res = self.query(
            "SELECT sqlite_version() as sqliteversion;")
        return [res.pgversion, res.pgisversion]
    
