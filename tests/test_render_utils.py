import sys
sys.path.append("./")
from hydrologis_utils.render_utils import HyGeomRenderer, HyStyle
from hydrologis_utils.geom_utils import HyGeomUtils
from hydrologis_utils.color_utils import HyColor
from shapely.geometry import Polygon, Point, box

import unittest


# run with python3 -m unittest discover tests/

class TestRenderUtils(unittest.TestCase):
    
    def test_polygon_tile(self):
        geom1Wkt = """MULTIPOLYGON (((110 420, 305 274, 580 480, 350 750, 140 720, 110 420)), 
                    ((460 280, 566 115, 766 195, 690 410, 460 280)), 
                    ((760 720, 950 140, 1120 710, 760 720)))"""
        geom2Wkt = """POLYGON ((300 -30, 280 160, 640 180, 660 40, 300 -30), 
                    (384 124, 400 30, 585 66, 570 140, 384 124))"""
        
        geom1 = HyGeomUtils.fromWkt(geom1Wkt)
        geom2 = HyGeomUtils.fromWkt(geom2Wkt)
                
        boundsGeom = HyGeomUtils.fromWkt("POLYGON ((200 700, 900 700, 900 0, 200 0, 200 700))")
        tile_bounds = boundsGeom.bounds
        # tile_bounds = (200, 0, 900, 700)  # (min_lat, min_lon, max_lat, max_lon)

        renderer = HyGeomRenderer(imageSize=(512, 512))
        renderer.setPolygonStyle(HyStyle(fillColor=HyColor(rgbaColor=(0,0,255,128)),strokeColor=HyColor(rgbaColor=(0,0,255,255)), strokeWidth=5))
        tileImage = renderer.renderTile( tile_bounds, [geom1, geom2])

        tileImage.show()


if __name__ == "__main__":
    unittest.main()