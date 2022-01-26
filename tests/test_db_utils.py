from hydrologis_utils.db_utils import *

from sqlalchemy import Table, Column, Integer, String, MetaData, select
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape


import unittest

# run with python3 -m unittest discover tests/

class TestDbUtils(unittest.TestCase):

    def setUp(self):
        self.url = DbType.SQLITE_MEM.url()

        self.db = SqliteDb(self.url, echo=False)
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

        self.assertFalse(self.db.has_table(table_name))

        self.db.create_table(test_table)

        self.assertTrue(self.db.has_table(table_name))


        tables = self.db.get_tables(do_order=True)
        self.assertEquals(len(tables), 1)
        self.assertEquals(tables[0], table_name)

        cols = self.db.get_table_columns(table_name)
        self.assertEquals(len(cols), 2)

        dataList = [
            {'name': 'Majeur'},
            {'name': 'Garde'},
            {'name': 'Orta'}
        ]
        self.db.insert(test_table, dataList)

        result = self.db.get_table_data(test_table)
        count  = 0
        for row in result:
            count += 1
        self.assertEquals(count, 3)

        result = self.db.get_table_data(test_table, limit=2)
        count  = 0
        for row in result:
            count += 1
        self.assertEquals(count, 2)
        
        result = self.db.get_table_data(table_name, where="name='Orta'")
        count  = 0
        for row in result:
            count += 1
        self.assertEquals(count, 1)

        # test views
        sql = f"create view {view_name} as select name from {table_name}"
        self.db.execute(sql)

        self.assertTrue(self.db.has_view(view_name))

        result = self.db.get_table_data(view_name, where="name='Orta'")
        count  = 0
        for row in result:
            count += 1
        self.assertEquals(count, 1)

        self.db.drop_table(view_name)
        self.assertFalse(self.db.has_view(view_name))



    def test_sqlite_spatial(self):        
        table_name = 'test'
        test_table = Table(table_name, self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String),
            Column('geom', Geometry('POLYGON', srid=4326))
        )

        self.assertFalse(self.db.has_table(table_name))

        self.db.create_table(test_table)

        self.assertTrue(self.db.has_table(table_name))


        tables = self.db.get_tables(do_order=True)
        self.assertEquals(len(tables), 1)
        self.assertEquals(tables[0], table_name)

        cols = self.db.get_table_columns(table_name)
        self.assertEquals(len(cols), 2)

        dataList = [
            {'name': 'Majeur', 'geom': 'SRID=4326;POLYGON((0 0,1 0,1 1,0 1,0 0))'},
            {'name': 'Garde', 'geom': 'SRID=4326;POLYGON((1 0,3 0,3 2,1 2,1 0))'},
            {'name': 'Orta', 'geom': 'SRID=4326;POLYGON((3 0,6 0,6 3,3 3,3 0))'}
        ]
        self.db.insert(test_table, dataList)

        result = self.db.get_table_data(test_table)
        count  = 0
        for row in result:
            count += 1
        self.assertEquals(count, 3)

        result = self.db.get_table_data(test_table, limit=2)
        count  = 0
        for row in result:
            count += 1
        self.assertEquals(count, 2)
        
        result = self.db.get_table_data(test_table, where="name='Orta'")
        count  = 0
        for row in result:
            count += 1
        self.assertEquals(count, 1)
        
        

        # views = db.get_views(do_order=True)
        # for view in views:
        #     print(view)

        # cols = db.get_table_columns(lake_table.name)
        # print(f"COLUMNS: {lake_table.name}")
        # for col in cols:
        #     print(col)
        
        # dataList = [
        #     {'name': 'Majeur', 'geom': 'SRID=4326;POLYGON((0 0,1 0,1 1,0 1,0 0))'},
        #     {'name': 'Garde', 'geom': 'SRID=4326;POLYGON((1 0,3 0,3 2,1 2,1 0))'},
        #     {'name': 'Orta', 'geom': 'SRID=4326;POLYGON((3 0,6 0,6 3,3 3,3 0))'}
        # ]
        # db.insert(lake_table, dataList)

        # #  conn.execute(Poi.__table__.insert(), [
        # #     {'geog': 'SRID=4326;POINT(1 1)'},
        # #     {'geog': WKTElement('POINT(1 1)', srid=4326)},
        # #     {'geog': WKTElement('SRID=4326;POINT(1 1)', extended=True)},
        # #     {'geog': from_shape(Point(1, 1), srid=4326)}
        # # ])


        # sel_obj  = select([lake_table])
        # result = db.select(sel_obj)
        # for row in result:
        #     geom = to_shape(row['geom'])
        #     area = db.decode(row['geom'].ST_Area())
        #     wkt = db.decode(row['geom'].ST_AsEWKT())
        #     print(f"{row[0]} - {geom}  - {area} - {wkt}")
        
        # # result = db.query("select * from lake")
        # # for row in result:
        # #     area = db.scalar(row['geom'].ST_Area())
        # #     wkt = db.scalar(row['geom'].ST_AsEWKT())
        # #     print(f"{row[0]} - {row[1]} - {area} - {wkt}")
        
  

if __name__ == "__main__":
    unittest.main()