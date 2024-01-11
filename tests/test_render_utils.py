import sys
sys.path.append("./")
from hydrologis_utils.render_utils import HyGeomRenderer, HyStyle
from hydrologis_utils.geom_utils import HyGeomUtils, ExtendedGeometry
from hydrologis_utils.color_utils import HyColor
from PIL import Image, ImageChops

import unittest


# run with python3 -m unittest discover tests/

class TestRenderUtils(unittest.TestCase):
    polygon1Wkt = """MULTIPOLYGON (((110 420, 305 274, 580 480, 350 750, 140 720, 110 420)), 
                ((460 280, 566 115, 766 195, 690 410, 460 280)), 
                ((760 720, 950 140, 1120 710, 760 720)))"""
    polygon2Wkt = """POLYGON ((300 -30, 280 160, 640 180, 660 40, 300 -30), 
                (384 124, 400 30, 585 66, 570 140, 384 124))"""
    line1Wkt = """MULTILINESTRING ((160 -30, 460 360, 110 450, 360 750, 570 530, 860 740, 1090 440, 630 360), 
                        (460 70, 510 340, 735 116, 770 490))"""
    line2Wkt = """LINESTRING (312 205, 490 520, 570 80, 790 600)"""
    point1Wkt = """MULTIPOINT ((440 190), (360 390), (660 510), (737 355))"""
    point2Wkt = """POINT (210 50)"""
    point3Wkt = """POINT (187 105)"""
    
    def test_polygon_tile(self):
        
        geom1 = HyGeomUtils.fromWkt(self.polygon1Wkt)
        geom2 = HyGeomUtils.fromWkt(self.polygon2Wkt)
                
        boundsGeom = HyGeomUtils.fromWkt("POLYGON ((200 700, 900 700, 900 0, 200 0, 200 700))")
        tile_bounds = boundsGeom.bounds

        renderer = HyGeomRenderer(imageSize=(512, 512))
        renderer.setPolygonStyle(HyStyle(fillColor=HyColor(rgbaColor=(0,0,255,128)),strokeColor=HyColor(rgbaColor=(0,0,255,255)), strokeWidth=5))
        tileImage = renderer.renderImage( tile_bounds, [geom1, geom2])

        # compare the image with this
        compareImage = "./tests/samples/test_tile_polygon.png"
        diff = ImageChops.difference(tileImage, Image.open(compareImage))
        self.assertIsNone(diff.getbbox())

        tileImage = renderer.renderImage( tile_bounds, [geom1, geom2], antialias=True)
        compareImage = "./tests/samples/test_tile_polygon_antialias.png"
        diff = ImageChops.difference(tileImage, Image.open(compareImage))
        self.assertIsNone(diff.getbbox())

        # style by attribute
        colorTable = {
            1:HyStyle(fillColor=HyColor(rgbaColor=(255,0,0,128)),strokeColor=HyColor(rgbaColor=(255,0,0,255)), strokeWidth=3), 
            2:HyStyle(fillColor=HyColor(rgbaColor=(0,255,0,128)),strokeColor=HyColor(rgbaColor=(0,255,0,255)), strokeWidth=3)
        }
        tileImage = renderer.renderImage( tile_bounds, [ExtendedGeometry(geom1, 1), ExtendedGeometry(geom2, 2)], colorTable=colorTable)
        compareImage = "./tests/samples/test_tile_polygon_styled.png"
        diff = ImageChops.difference(tileImage, Image.open(compareImage))
        self.assertIsNone(diff.getbbox())


    
    def test_line_tile(self):
        geom1 = HyGeomUtils.fromWkt(self.line1Wkt)
        geom2 = HyGeomUtils.fromWkt(self.line2Wkt)
                
        boundsGeom = HyGeomUtils.fromWkt("POLYGON ((200 700, 900 700, 900 0, 200 0, 200 700))")
        tile_bounds = boundsGeom.bounds

        renderer = HyGeomRenderer(imageSize=(512, 512))
        renderer.setLineStyle(HyStyle(strokeColor=HyColor(rgbaColor=(0,0,255,255)), strokeWidth=5))
        tileImage = renderer.renderImage( tile_bounds, [geom1, geom2])

        compareImage = "./tests/samples/test_tile_line.png"
        # compare the image with this
        diff = ImageChops.difference(tileImage, Image.open(compareImage))
        self.assertIsNone(diff.getbbox())
    
    def test_point_tile(self):     
        geom1 = HyGeomUtils.fromWkt(self.point1Wkt)
        geom2 = HyGeomUtils.fromWkt(self.point2Wkt)
        geom3 = HyGeomUtils.fromWkt(self.point3Wkt)
                
        boundsGeom = HyGeomUtils.fromWkt("POLYGON ((200 700, 900 700, 900 0, 200 0, 200 700))")
        tile_bounds = boundsGeom.bounds

        renderer = HyGeomRenderer(imageSize=(512, 512))
        
        # style by attribute
        colorTable = {
            1:HyStyle(fillColor=HyColor(rgbaColor=(255,0,0,128)),strokeColor=HyColor(rgbaColor=(255,0,0,255)), strokeWidth=1, size=30), 
            2:HyStyle(fillColor=HyColor(rgbaColor=(0,255,0,128)),strokeColor=HyColor(rgbaColor=(0,255,0,255)), strokeWidth=1, size=30),
            3:HyStyle(fillColor=HyColor(rgbaColor=(0,0,255,128)),strokeColor=HyColor(rgbaColor=(0,0,255,255)), strokeWidth=1, size=50)
        }
        tileImage = renderer.renderImage( tile_bounds, [ExtendedGeometry(geom1, 1), ExtendedGeometry(geom2, 2), ExtendedGeometry(geom3, 3)], colorTable=colorTable, \
                                         intersectionBufferX=20)

        compareImage = "./tests/samples/test_tile_point.png"
        # compare the image with this
        diff = ImageChops.difference(tileImage, Image.open(compareImage))
        self.assertIsNone(diff.getbbox())

    def test_misch_tile(self):     
        geom1 = HyGeomUtils.fromWkt(self.polygon1Wkt)
        geom2 = HyGeomUtils.fromWkt(self.polygon2Wkt)
        geom3 = HyGeomUtils.fromWkt(self.line1Wkt)
        geom4 = HyGeomUtils.fromWkt(self.line2Wkt)
        geom5 = HyGeomUtils.fromWkt(self.point1Wkt)
        geom6 = HyGeomUtils.fromWkt(self.point2Wkt)
        geom7 = HyGeomUtils.fromWkt(self.point3Wkt)
                
        boundsGeom = HyGeomUtils.fromWkt("POLYGON ((200 700, 900 700, 900 0, 200 0, 200 700))")
        tile_bounds = boundsGeom.bounds

        renderer = HyGeomRenderer(imageSize=(512, 512))
        
        # style by attribute
        colorTable = {
            "points":HyStyle(fillColor=HyColor(rgbaColor=(255,0,0,180)),strokeColor=HyColor(rgbaColor=(255,0,0,255)), strokeWidth=1, size=50), 
            "lines":HyStyle(strokeColor=HyColor(rgbaColor=(0,255,0,255)), strokeWidth=3),
            "polygons":HyStyle(fillColor=HyColor(rgbaColor=(0,0,255,180)),strokeColor=HyColor(rgbaColor=(0,0,255,255)), strokeWidth=2), 
        }
        tileImage = renderer.renderImage( tile_bounds, [
            ExtendedGeometry(geom1, "polygons"), 
            ExtendedGeometry(geom2, "polygons"),
            ExtendedGeometry(geom3, "lines"), 
            ExtendedGeometry(geom4, "lines"),
            ExtendedGeometry(geom5, "points"), 
            ExtendedGeometry(geom6, "points"),
            ExtendedGeometry(geom7, "points"),
            ], colorTable=colorTable, antialias=True, intersectionBufferX=20)

        compareImage = "./tests/samples/test_tile_misch.png"
        # compare the image with this
        diff = ImageChops.difference(tileImage, Image.open(compareImage))
        self.assertIsNone(diff.getbbox())


if __name__ == "__main__":
    unittest.main()