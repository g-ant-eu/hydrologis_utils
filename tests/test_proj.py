from hydrologis_utils.geom_utils import HyGeomUtils
from hydrologis_utils.proj_utils import HyProjManager

import unittest

# run with python3 -m unittest discover tests/

class TestProjtils(unittest.TestCase):
    def test_wkt_conv(self):
        # create a wkt of a Linstring
        wktPoint = "POINT (30 10)"
        wktLine = "LINESTRING (30 10, 10 30, 40 40)"
        ewktLine = "SRID=4326;LINESTRING (30 10, 10 30, 40 40)"
        point = HyGeomUtils.fromWkt(wktPoint)
        line1 = HyGeomUtils.fromWkt(wktLine)
        line2 = HyGeomUtils.fromWkt(ewktLine)

        pm = HyProjManager( 4326, 3857 )
        point = pm.transform(point)
        self.assertTrue(point.equals_exact(HyGeomUtils.fromWkt("POINT (3339584.723798207 1118889.9748579594)"), 0.000001))
        line1 = pm.transform(line1)
        self.assertTrue(line1.equals_exact(HyGeomUtils.fromWkt("LINESTRING (3339584.723798207 1118889.9748579594, 1113194.9079327357 3503549.8435043753, 4452779.631730943 4865942.279503175)"), 0.000001))
        line2 = pm.transform(line2)
        self.assertTrue(line2.equals_exact(line1, 0.000001))

if __name__ == "__main__":
    unittest.main()