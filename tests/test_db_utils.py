from hydrologis_utils.db_utils import *

from sqlalchemy import Table, Column, Integer, String, MetaData, select
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape
from sqlalchemy.sql import text
import shapely.wkb as wkb
import tempfile



import unittest

# run with python3 -m unittest discover tests/

class TestDbUtils(unittest.TestCase):

    def setUp(self):
        self.url = DbType.SQLITE_MEM.url()

        self.db = SqliteDb(self.url, echo=True)
        self.metadata = MetaData()
            

    def test_col(self):
        col = DbColumn(name="test", is_autoincrement=False, blah="blu")
        self.assertEqual(col.name, "test")

        args = {
            "name":"test", 
            "is_autoincrement":False, 
            "blah":"blu"
        }
        col = DbColumn(**args)
        self.assertEqual(col.name, "test")

    
    def test_sqlite(self):
        table_name = 'test'
        view_name = 'testview'

        test_table = Table(table_name, self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String)
        )

        self.assertFalse(self.db.hasTable(table_name))

        self.db.createTable(test_table)

        self.assertTrue(self.db.hasTable(table_name))


        tables = self.db.getTables(do_order=True)
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0], table_name)

        cols = self.db.getTableColumns(table_name)
        self.assertEqual(len(cols), 2)

        dataList = [
            {'name': 'Majeur'},
            {'name': 'Garde'},
            {'name': 'Orta'}
        ]
        self.db.insert(test_table, dataList)

        with self.db.connect() as conn:
            result = conn.execute("select * from test")
        
        for row in result:
            print(row['name'])

        result = self.db.getTableData(test_table)
        count  = 0
        for row in result:
            count += 1
        self.assertEquals(count, 3)

        result = self.db.getTableData(test_table, limit=2)
        count  = 0
        for row in result:
            count += 1
        self.assertEquals(count, 2)
        
        result = self.db.getTableData(table_name, where="name='Orta'")
        count  = 0
        for row in result:
            count += 1
        self.assertEquals(count, 1)

        # test views
        sql = f"create view {view_name} as select name from {table_name}"
        self.db.execute(sql)

        self.assertTrue(self.db.hasView(view_name))

        result = self.db.getTableData(view_name, where="name='Orta'")
        count  = 0
        for row in result:
            count += 1
        self.assertEquals(count, 1)

        self.db.dropTable(view_name)
        self.assertFalse(self.db.hasView(view_name))



    # def test_sqlite_spatial(self):        
    #     table_name = 'test'
    #     test_table = Table(table_name, self.metadata,
    #         Column('id', Integer, primary_key=True),
    #         Column('name', String),
    #         Column('geom', Geometry('POLYGON', srid=4326))
    #     )

    #     self.assertFalse(self.db.hasTable(table_name))

    #     self.db.createTable(test_table)

    #     self.assertTrue(self.db.hasTable(table_name))


    #     tables = self.db.getTables(do_order=True)
    #     self.assertEquals(len(tables), 1)
    #     self.assertEquals(tables[0], table_name)

    #     cols = self.db.getTableColumns(table_name)
    #     self.assertEquals(len(cols), 2)

    #     dataList = [
    #         {'name': 'Majeur', 'geom': 'SRID=4326;POLYGON((0 0,1 0,1 1,0 1,0 0))'},
    #         {'name': 'Garde', 'geom': 'SRID=4326;POLYGON((1 0,3 0,3 2,1 2,1 0))'},
    #         {'name': 'Orta', 'geom': 'SRID=4326;POLYGON((3 0,6 0,6 3,3 3,3 0))'}
    #     ]
    #     self.db.insert(test_table, dataList)

    #     result = self.db.getTableData(test_table)
    #     count  = 0
    #     for row in result:
    #         count += 1
    #     self.assertEquals(count, 3)

    #     result = self.db.getTableData(test_table, limit=2)
    #     count  = 0
    #     for row in result:
    #         count += 1
    #     self.assertEquals(count, 2)
        
    #     result = self.db.getTableData(test_table, where="name='Orta'")
    #     count  = 0
    #     for row in result:
    #         count += 1
    #     self.assertEquals(count, 1)
        

    # def test_sqlite_geopackage(self):    
    #     # get path of file inside tests folder

    #     current_dir = os.path.dirname(os.path.abspath(__file__))
    #     path = os.path.join(current_dir, 'samples', 'gdal_sample.gpkg')
    #     url = DbType.GPKG.url(dbname=path)
    #     db = GpkgDb(url, echo=False)

    #     table = "point2d"
    #     gc = db.getGeometryColumn(table)
    #     self.assertEqual(gc.name, "geom")
    #     self.assertEqual(gc.geoinfo.srid, -1)

    #     count = db.getRecordCount(table)
    #     self.assertEqual(count, 1)


    #     with db.connect() as conn:
    #         result = conn.execute(text(f"select geom from {table}"))
    #         geom = result.first()[0]
    #         sgeom = wkb.loads(geom, hex=True)
            
    #         print(type(geom))
            
    def test_spatialite_generation_and_inserts(self):
        # create a spatialite file in the os tmp folder
        tmp_dir = tempfile.gettempdir()
        dbPath = os.path.join(tmp_dir, "test_spatialite.sqlite")
        if os.path.exists(dbPath):
            os.remove(dbPath)
        number = 10000

        url = DbType.SPATIALITE.url(dbname=dbPath)
        db = SpatialiteDb(url, echo=False)

        # create a spatial lines table
        table_name = "lines"
        table = Table(table_name, self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String),
            Column('geom', Geometry('LINESTRING', srid=4326))
        )
        db.createTable(table)

        # insert many lines to test performance
        for i in range(0, number):
            line = {
                "name": f"line {i}",
                "geom": f"SRID=4326;LINESTRING({i} {i},{i+1} {i+1})"
            }
            rowcount = db.insertOrmWithParams(table, line)
            self.assertEqual(rowcount, 1)
        
        data = db.getTableData(table_name)
        self.assertEqual(len(data), number)

        table_name = "bulklines"
        table = Table(table_name, self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String),
            Column('geom', Geometry('LINESTRING', srid=4326))
        )
        db.createTable(table)

        # insert many lines to test performance
        lines = []
        for i in range(0, number):
            line = {
                "name": f"line {i}",
                "geom": f"SRID=4326;LINESTRING({i} {i},{i+1} {i+1})"
            }
            lines.append(line)

        rowcount = db.insertOrmWithParams(table, lines)
        self.assertEqual(rowcount, number)


        # now do the same with execute without table

        table_name = "execlines"
        table = Table(table_name, self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String),
            Column('geom', Geometry('LINESTRING', srid=4326))
        )
        db.createTable(table)

        # insert many lines to test performance
        lines = []
        for i in range(0, number):
            line = {
                "name": f"line {i}",
                "geom": f"LINESTRING({i} {i},{i+1} {i+1})"
            }
            lines.append(line)

        sql = f"INSERT INTO {table_name} (name, geom) VALUES (:name, ST_geomfromtext(:geom, 4326))"

        rowcount = db.insertSqlWithParams(sql, lines)
        self.assertEqual(rowcount, number)


        os.remove(dbPath)



  

if __name__ == "__main__":
    unittest.main()