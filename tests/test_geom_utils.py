from hydrologis_utils.geom_utils import HyGeomUtils, HySTRTreeIndex
from shapely.affinity import affine_transform
from shapely.geometry import GeometryCollection, LineString, MultiLineString, MultiPoint, MultiPolygon, Point, Polygon
import unittest

# run with python3 -m unittest discover tests/

class TestGeomutils(unittest.TestCase):
    
    # test fromWkt and toWkt methods
    def test_wkt_conv(self):
        # create a wkt of a Linstring
        wkt = "LINESTRING (30 10, 10 30, 40 40)"
        wktWithEpsg = "SRID=4326;LINESTRING (30 10, 10 30, 40 40)"
        # convert to shapely geometry
        geom = HyGeomUtils.fromWkt(wkt, srid=4326)
        # convert back to wkt
        wkt2 = HyGeomUtils.toWkt(geom)
        self.assertEqual(HyGeomUtils.fromWkt(wktWithEpsg), HyGeomUtils.fromWkt(wkt2))


        geom1 = HyGeomUtils.fromWkt(wktWithEpsg)
        wkb = HyGeomUtils.toWkb(geom)
        # convert back to geom
        geom2 = HyGeomUtils.fromWkb(wkb)
        
        self.assertEqual(geom, geom2)
        self.assertEqual(geom1, geom2)

    def test_extended(self):
        # create a wkt of a Linstring
        wkt = "LINESTRING (30 10, 10 30, 40 40)"
        extGeom = HyGeomUtils.fromWkt(wkt, extended=True)
        self.assertIsNone(extGeom.get_srid())

        extGeom.set_srid(4326)
        self.assertEqual(extGeom.get_srid(), 4326)

    def test_extended_geom_creation(self):
        extGeom = HyGeomUtils.makePoint([30, 10], srid=4326, extended=True)
        self.assertIsInstance(extGeom.get_basegeometry(), Point)
        self.assertEqual(extGeom.get_srid(), 4326)

        extGeom = HyGeomUtils.makeLineString([[30, 10], [10, 30], [40, 40]], srid=4326, extended=True)
        self.assertIsInstance(extGeom.get_basegeometry(), LineString)
        self.assertEqual(extGeom.get_srid(), 4326)

        extGeom = HyGeomUtils.makePolygon([[30, 10], [10, 30], [40, 40]], srid=4326, extended=True)
        self.assertIsInstance(extGeom.get_basegeometry(), Polygon)
        self.assertEqual(extGeom.get_srid(), 4326)


    def test_geom_2d(self):
        # create a 3d Linestring wkt
        wkt = "LINESTRING Z (30 10 1, 10 30 2, 40 40 3)"
        geom3D = HyGeomUtils.fromWkt(wkt)

        # convert to 2d
        geom2D = HyGeomUtils.convert2D(geom3D)

        wkt2D = "LINESTRING (30 10, 10 30, 40 40)"
        geom2Dexp = HyGeomUtils.fromWkt(wkt2D)

        self.assertEqual(geom2D, geom2Dexp)

    def test_split_line(self):
        wkt = "LINESTRING (0 0, 10 0, 10 10, 18 10)"
        geom = HyGeomUtils.fromWkt(wkt)
        lines = HyGeomUtils.splitLineEquidistant(geom, 5)
        self.assertEqual(len(lines), 6)

        for line in lines[:-1]:
            self.assertEqual(line.length, 5)
        self.assertEqual(lines[-1].length, 3)

        wkt = "MULTILINESTRING ((680372.6569 4936651.3185 0,680385.5099 4936690.8508 0,680394.8311 4936687.6387 0,680382.0701 4936648.0783 0,680372.6569 4936651.3185 0))"
        geom = HyGeomUtils.fromWkt(wkt)
        geom = HyGeomUtils.joinLines(geom)
        geom = HyGeomUtils.convert2D(geom)

        delta = geom.length % 3
        pieces = (geom.length-delta)/3 + 1
        lines = HyGeomUtils.splitLineEquidistant(geom, 3)
        self.assertEqual(len(lines), pieces)

        

        
    # test joinLines method
    def test_join_lines(self):
        # create a wkt of a Linstring
        wkt1 = "LINESTRING (30 10, 10 30, 40 40)"
        wkt2 = "LINESTRING (40 40, 50 40, 50 30)"
        wkt3 = "LINESTRING (41 40, 50 40, 50 30)"
        joinWkt = "LINESTRING (30 10, 10 30, 40 40, 50 40, 50 30)"
        # convert to shapely geometry
        geom1 = HyGeomUtils.fromWkt(wkt1)
        geom2 = HyGeomUtils.fromWkt(wkt2)
        geom3 = HyGeomUtils.fromWkt(wkt3)
        joinGeom = HyGeomUtils.fromWkt(joinWkt)

        # join the two lines
        lines = [geom1, geom2]
        mergedLine = HyGeomUtils.joinLines(lines)

        self.assertEqual(mergedLine.length,  geom1.length+geom2.length)
        self.assertEqual(mergedLine, joinGeom)

        # join the two lines
        lines = [geom1, geom3]
        mergedLine = HyGeomUtils.joinLines(lines)

        self.assertEqual(len(mergedLine.geoms), 2)


    def test_to_geojson(self):
        # create a wkt of a Linstring
        wkt = "SRID=4326;MULTILINESTRING ((10.9823496053121 44.1270461245985, 10.9826260483698 44.1271185726098, 10.9827005016574 44.1271569262385, 10.9828179452725 44.1272174274885, 10.9830390596593 44.127384537057))"
        # convert to shapely geometry
        geom = HyGeomUtils.fromWkt(wkt)

        # convert to geojson
        geojson = HyGeomUtils.toGeoJson(geom)

        # convert back to geom
        geom2 = HyGeomUtils.fromGeoJson(geojson)
        
        self.assertEqual(geom, geom2)

    def test_spatial_index_query(self):

        p1 = HyGeomUtils.fromWkt("POINT (100 100)")
        p2 = HyGeomUtils.fromWkt("POINT (200 150)")
        p3 = HyGeomUtils.fromWkt("POINT (320 200)")

        line = HyGeomUtils.fromWkt("LINESTRING (100 200, 300 200, 300 130)")

        index = HySTRTreeIndex([p1, p2, p3])

        geoms = index.query(line)
        self.assertEqual(len(geoms), 1)
        self.assertEqual(geoms[0], p2)

        # now with reference list
        index = HySTRTreeIndex([p1, p2, p3], [1, 2, 3])
        refList = index.query(line)
        self.assertEqual(len(refList), 1)
        self.assertEqual(refList[0], 2)

    def test_spatial_index_nearest(self):
        p1 = HyGeomUtils.fromWkt("POINT (100 100)")
        p2 = HyGeomUtils.fromWkt("POINT (200 150)")
        p3 = HyGeomUtils.fromWkt("POINT (320 200)")

        line = HyGeomUtils.fromWkt("LINESTRING (100 200, 300 200, 300 130)")

        index = HySTRTreeIndex([p1, p2, p3])

        geom = index.queryNearest(line, maxDistance=1000)
        self.assertEqual(geom, p3)
        
        geom = index.queryNearest(line, maxDistance=10)
        self.assertIsNone(geom)
        
        geom = index.queryNearest(line)
        self.assertEqual(geom, p3)

        # now with reference list
        index = HySTRTreeIndex([p1, p2, p3], [1, 2, 3])
        ref = index.queryNearest(line)
        self.assertEqual(ref, 3)

    def test_transform_world_to_rectangle(self):
        world = (100, 1000, 200, 5000)
        rect = (0, 0, 100, 4000)

        matrix = HyGeomUtils.worldToRectangleMatrix(world, rect)
        
        p = Point(150.0, 3000.0)
        transformedP = affine_transform(p, matrix)
        self.assertEqual(transformedP.x, 50)
        self.assertEqual(transformedP.y, 2000)
        
        p = Point(100.0, 1000.0)
        transformedP = affine_transform(p, matrix)
        self.assertEqual(transformedP.x, 0)
        self.assertEqual(transformedP.y, 4000)
    


if __name__ == "__main__":
    unittest.main()