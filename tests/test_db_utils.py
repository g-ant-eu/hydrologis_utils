from hydrologis_utils.db_utils import *

from sqlalchemy import Table, Column, Integer, String, MetaData, select
from geoalchemy2 import Geometry

import unittest

# run with python3 -m unittest discover tests/

class TestStrings(unittest.TestCase):
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

    
    def test_posgres(self):
        db_host = 'localhost'
        db_port = '5432'
        db_name = 'test'
        db_user = 'postgres'
        db_password = 'postgres'

        url = DbType.POSTGRESQL.url(dbname=db_name, host=db_host, port=db_port, user=db_user, pwd=db_password)

        db = PostgresDb(url, echo=False)
        tables = db.get_tables(do_order=True)
        for tabel in tables:
            print(tabel)

        tname = "django_content_type"

        cols = db.get_table_columns(tname)
        print(f"COLUMNS: {tname}")
        for col in cols:
            print(col)
        
        result = db.get_table(tname)
        # for row in result:
        #     print(row)

        metadata = MetaData()
        lake_table = Table('lake', metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String),
            Column('geom', Geometry('POLYGON', srid=4326))
        )

        if db.has_table(lake_table.name):
            db.drop_table(lake_table)

        db.create_table(lake_table)
        
        dataList = [
            {'name': 'Majeur', 'geom': 'SRID=4326;POLYGON((0 0,1 0,1 1,0 1,0 0))'},
            {'name': 'Garde', 'geom': 'SRID=4326;POLYGON((1 0,3 0,3 2,1 2,1 0))'},
            {'name': 'Orta', 'geom': 'SRID=4326;POLYGON((3 0,6 0,6 3,3 3,3 0))'}
        ]
        db.insert(lake_table, dataList)


        sel_obj  = select([lake_table])
        result = db.select(sel_obj)
        for row in result:
            area = db.scalar(row['geom'].ST_Area())
            wkt = db.scalar(row['geom'].ST_AsEWKT())
            print(f"{row[0]} - {row[1]} - {area} - {wkt}")
        
        result = db.query("select * from lake")
        for row in result:
            area = db.scalar(row['geom'].ST_Area())
            wkt = db.scalar(row['geom'].ST_AsEWKT())
            print(f"{row[0]} - {row[1]} - {area} - {wkt}")
        
  

if __name__ == "__main__":
    unittest.main()