from shapely.geometry import Polygon, Point, box
from PIL import Image, ImageDraw
from shapely.geometry.base import BaseGeometry
from shapely.affinity import affine_transform
from hydrologis_utils.geom_utils import HyGeomUtils
from hydrologis_utils.color_utils import HyColor

class HyStyle():
    def __init__(self, fillColor:HyColor = None, strokeColor:HyColor = None, strokeWidth:int = 2):
        self.fillColor = fillColor
        self.strokeColor = strokeColor
        self.strokeWidth = strokeWidth

    @staticmethod
    def defaultPolygonStyle():
        return HyStyle(fillColor=HyColor(rgbaColor=(255,0,0,100)),strokeColor=HyColor(rgbaColor=(255,0,0,255)), strokeWidth=2)
    
    @staticmethod
    def defaultLineStyle():
        return HyStyle(strokeColor=HyColor(rgbaColor=(255,0,0,255)), strokeWidth=2)

class HyGeomRenderer():
    """
    Small utility to draw geometries on images.
    """
    def __init__(self, imageSize:(int, int)):
        self.imageSize = imageSize
        self.polygonStyle = HyStyle.defaultPolygonStyle()
        self.lineStyle = HyStyle.defaultLineStyle()

    def setPolygonStyle(self, style:HyStyle):
        self.polygonStyle = style
    
    def setLineStyle(self, style:HyStyle):
        self.lineStyle = style

    def renderTile(self, tileBoundsLongLat:[float], geometries:[BaseGeometry] , antialias:bool=False) -> Image:
        # Create a bounding box geometry for the tile
        tile_box = box(tileBoundsLongLat[0], tileBoundsLongLat[1], tileBoundsLongLat[2], tileBoundsLongLat[3])


        factor = 1
        if antialias:
            factor = 2
        # Create a transparent image
        w = self.imageSize[0]*factor
        h = self.imageSize[1]*factor
        
        image = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        # Create a drawing object
        draw = ImageDraw.Draw(image)

        for geom in geometries:
            if geom.intersects(tile_box):
                matrix = HyGeomUtils.worldToRectangleMatrix([tileBoundsLongLat[0], tileBoundsLongLat[1], tileBoundsLongLat[2], tileBoundsLongLat[3]], [0, 0, w, h])
                scaledGeom = affine_transform(geom, matrix)

                if scaledGeom.geom_type == "Polygon":
                    draw.polygon(scaledGeom.exterior.coords, outline=self.polygonStyle.strokeColor.getRgba(), fill=self.polygonStyle.fillColor.getRgba(), width=self.polygonStyle.strokeWidth*factor)
                    for hole in scaledGeom.interiors:
                        draw.polygon(hole.coords, outline=self.polygonStyle.strokeColor.getRgba(), fill=(0, 0, 0, 0), width=self.polygonStyle.strokeWidth*factor)
                elif scaledGeom.geom_type == "MultiPolygon":
                    for poly in scaledGeom.geoms:
                        draw.polygon(poly.exterior.coords, outline=self.polygonStyle.strokeColor.getRgba(), fill=self.polygonStyle.fillColor.getRgba(), width=self.polygonStyle.strokeWidth*factor)
                        for hole in poly.interiors:
                            draw.polygon(hole.coords, outline=self.polygonStyle.strokeColor.getRgba(), fill=(0, 0, 0, 0), width=self.polygonStyle.strokeWidth*factor)
                elif scaledGeom.geom_type == "LineString":
                    draw.line(scaledGeom.coords, fill=self.polygonStyle.strokeColor.getRgba(), width=self.polygonStyle.strokeWidth*factor)
                elif scaledGeom.geom_type == "MultiLineString":
                    for line in scaledGeom.geoms:
                        draw.line(line.coords, fill=self.polygonStyle.strokeColor.getRgba(), width=self.polygonStyle.strokeWidth*factor)

        if antialias:
            image = image.resize(self.imageSize, Image.Resampling.LANCZOS)

        return image
