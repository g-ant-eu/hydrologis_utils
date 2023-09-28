from hydrologis_utils.geom_utils import HyGeomUtils

import unittest

# run with python3 -m unittest discover tests/

class TestGeomutils(unittest.TestCase):
    
    # test fromWkt and toWkt methods
    def test_wkt_conv(self):
        # create a wkt of a Linstring
        wkt = "LINESTRING (30 10, 10 30, 40 40)"
        # convert to shapely geometry
        geom = HyGeomUtils.fromWkt(wkt)

        wkb = HyGeomUtils.toWkb(geom)
        # convert back to geom
        geom2 = HyGeomUtils.fromWkb(wkb)
        
        self.assertEqual(geom, geom2)


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
        self.assertEquals(len(lines), 6)

        for line in lines[:-1]:
            self.assertEquals(line.length, 5)
        self.assertEquals(lines[-1].length, 3)

        wkt = "MULTILINESTRING ((680372.6569 4936651.3185 0,680385.5099 4936690.8508 0,680394.8311 4936687.6387 0,680382.0701 4936648.0783 0,680372.6569 4936651.3185 0))"
        geom = HyGeomUtils.fromWkt(wkt)
        geom = HyGeomUtils.joinLines(geom)
        geom = HyGeomUtils.convert2D(geom)

        delta = geom.length % 3
        pieces = (geom.length-delta)/3 + 1
        lines = HyGeomUtils.splitLineEquidistant(geom, 3)
        self.assertEquals(len(lines), pieces)

        

        
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


    


    




if __name__ == "__main__":
    unittest.main()