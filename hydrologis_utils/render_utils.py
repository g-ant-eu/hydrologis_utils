from shapely.geometry import Polygon, Point, box
from PIL import Image, ImageDraw
from shapely.geometry.base import BaseGeometry
from shapely.affinity import affine_transform
from hydrologis_utils.geom_utils import HyGeomUtils, ExtendedGeometry
from hydrologis_utils.color_utils import HyColor
import math

class HyStyle():
    def __init__(self, fillColor:HyColor = None, strokeColor:HyColor = None, strokeWidth:int = 2, size:int = 15):
        self.fillColor = fillColor
        self.strokeColor = strokeColor
        self.strokeWidth = strokeWidth
        self.size = size

    @staticmethod
    def defaultPolygonStyle():
        return HyStyle(fillColor=HyColor(rgbaColor=(255,0,0,100)),strokeColor=HyColor(rgbaColor=(255,0,0,255)), strokeWidth=2)
    
    @staticmethod
    def defaultLineStyle():
        return HyStyle(strokeColor=HyColor(rgbaColor=(255,0,0,255)), strokeWidth=2)
    
    @staticmethod
    def defaultPointStyle():
        return HyStyle(fillColor=HyColor(rgbaColor=(255,0,0,100)),strokeColor=HyColor(rgbaColor=(255,0,0,255)), strokeWidth=1, size=15)

class HySlippyTiles():
    @staticmethod
    def tile2lon( x:int, zoom:int ):
        return x / pow(2.0, zoom) * 360.0 - 180.0
    
    @staticmethod
    def tile2lat( y:int, zoom:int ):
        n = math.pi - (2.0 * math.pi * y) / pow(2.0, zoom)
        return math.degrees(math.atan(math.sinh(n)))
    
    

class HyGeomRenderer():
    """
    Small utility to draw lat long geometries on an image.

    Usefull to create simple tiles.
    """
    def __init__(self, imageSize:(int, int)):
        self.imageSize = imageSize
        self.polygonStyle = HyStyle.defaultPolygonStyle()
        self.lineStyle = HyStyle.defaultLineStyle()
        self.pointStyle = HyStyle.defaultPointStyle()

    def setPolygonStyle(self, style:HyStyle):
        self.polygonStyle = style
    
    def setLineStyle(self, style:HyStyle):
        self.lineStyle = style

    def setPointStyle(self, style:HyStyle):
        self.pointStyle = style

    def renderImage(self, imagesBoundsLongLat:[float], geometriesLongLat:[], colorTable:dict=None , antialias:bool=False) -> Image:
        # Create a bounding box geometry for the tile
        tile_box = box(imagesBoundsLongLat[0], imagesBoundsLongLat[1], imagesBoundsLongLat[2], imagesBoundsLongLat[3])

        factor = 1
        if antialias:
            factor = 2
        # Create a transparent image
        w = self.imageSize[0]*factor
        h = self.imageSize[1]*factor
        
        image = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        # Create a drawing object
        draw = ImageDraw.Draw(image)

        for geom in geometriesLongLat:
            if isinstance(geom, ExtendedGeometry):
                attribute = geom.attribute
                geom = geom.geom
            if geom.intersects(tile_box):
                matrix = HyGeomUtils.worldToRectangleMatrix([imagesBoundsLongLat[0], imagesBoundsLongLat[1], imagesBoundsLongLat[2], imagesBoundsLongLat[3]], [0, 0, w, h])
                scaledGeom = affine_transform(geom, matrix)

                style = self.polygonStyle
                # check if the geometry has an attribute to use with the colortable
                if colorTable and attribute and attribute in colorTable:
                    style = colorTable[attribute]

                if scaledGeom.geom_type == "Polygon":
                    draw.polygon(scaledGeom.exterior.coords, outline=style.strokeColor.getRgba(), fill=style.fillColor.getRgba(), width=style.strokeWidth*factor)
                    for hole in scaledGeom.interiors:
                        draw.polygon(hole.coords, outline=style.strokeColor.getRgba(), fill=(0, 0, 0, 0), width=style.strokeWidth*factor)
                elif scaledGeom.geom_type == "MultiPolygon":
                    for poly in scaledGeom.geoms:
                        draw.polygon(poly.exterior.coords, outline=style.strokeColor.getRgba(), fill=style.fillColor.getRgba(), width=style.strokeWidth*factor)
                        for hole in poly.interiors:
                            draw.polygon(hole.coords, outline=style.strokeColor.getRgba(), fill=(0, 0, 0, 0), width=style.strokeWidth*factor)
                elif scaledGeom.geom_type == "LineString":
                    draw.line(scaledGeom.coords, fill=style.strokeColor.getRgba(), width=style.strokeWidth*factor)
                elif scaledGeom.geom_type == "MultiLineString":
                    for line in scaledGeom.geoms:
                        draw.line(line.coords, fill=style.strokeColor.getRgba(), width=style.strokeWidth*factor)
                elif scaledGeom.geom_type == "Point":
                    halfSize = style.size/2
                    draw.ellipse([scaledGeom.x-halfSize, scaledGeom.y-halfSize, scaledGeom.x+halfSize, scaledGeom.y+halfSize], fill=style.fillColor.getRgba(), outline=style.strokeColor.getRgba(), width=style.strokeWidth*factor)
                elif scaledGeom.geom_type == "MultiPoint":
                    halfSize = style.size/2
                    for point in scaledGeom.geoms:
                        draw.ellipse([point.x-halfSize, point.y-halfSize, point.x+halfSize, point.y+halfSize], fill=style.fillColor.getRgba(), outline=style.strokeColor.getRgba(), width=style.strokeWidth*factor)
                        
        del draw
        if antialias:
            image = image.resize(self.imageSize, Image.Resampling.LANCZOS)

        return image
    
    @staticmethod
    def transparentImage(self) -> Image:
        return Image.new("RGBA", self.imageSize, (0, 0, 0, 0))
