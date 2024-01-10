from shapely.geometry import Polygon, Point, box
from PIL import Image, ImageDraw
from shapely.geometry.base import BaseGeometry
from shapely.affinity import affine_transform
from hydrologis_utils.geom_utils import HyGeomUtils
from hydrologis_utils.color_utils import HyColor

class HyStyle():
    def __init__(self, fillColor:HyColor, strokeColor:HyColor, strokeWidth:int):
        self.fillColor = fillColor
        self.strokeColor = strokeColor
        self.strokeWidth = strokeWidth

class HyGeomRenderer():
    """
    Small utility to draw geometries on images.
    """
    def __init__(self, imageSize:(int, int)):
        self.imageSize = imageSize
        self.polygonStyle = HyStyle(fillColor=HyColor(rgbaColor=(255,0,0,100)),strokeColor=HyColor(rgbaColor=(255,0,0,255)), strokeWidth=2)

    def setPolygonStyle(self, style:HyStyle):
        self.polygonStyle = style

    def renderTile(self, tileBoundsLongLat:[float], geometries:[BaseGeometry] ) -> Image:
        # Create a bounding box geometry for the tile
        tile_box = box(tileBoundsLongLat[0], tileBoundsLongLat[1], tileBoundsLongLat[2], tileBoundsLongLat[3])

        # Create a transparent image
        image = Image.new("RGBA", self.imageSize, (0, 0, 0, 0))
        # Create a drawing object
        draw = ImageDraw.Draw(image)

        for geom in geometries:
            if geom.intersects(tile_box):
                matrix = HyGeomUtils.worldToRectangleMatrix([tileBoundsLongLat[0], tileBoundsLongLat[1], tileBoundsLongLat[2], tileBoundsLongLat[3]], [0, 0, self.imageSize[0], self.imageSize[1]])
                scaledGeom = affine_transform(geom, matrix)

                if scaledGeom.geom_type == "Polygon":
                    draw.polygon(scaledGeom.exterior.coords, outline=self.polygonStyle.strokeColor.getRgba(), fill=self.polygonStyle.fillColor.getRgba(), width=self.polygonStyle.strokeWidth)
                    for hole in scaledGeom.interiors:
                        draw.polygon(hole.coords, outline=self.polygonStyle.strokeColor.getRgba(), fill=(0, 0, 0, 0), width=self.polygonStyle.strokeWidth)
                elif scaledGeom.geom_type == "MultiPolygon":
                    for poly in scaledGeom.geoms:
                        draw.polygon(poly.exterior.coords, outline=self.polygonStyle.strokeColor.getRgba(), fill=self.polygonStyle.fillColor.getRgba(), width=self.polygonStyle.strokeWidth)
                        for hole in poly.interiors:
                            draw.polygon(hole.coords, outline=self.polygonStyle.strokeColor.getRgba(), fill=(0, 0, 0, 0), width=self.polygonStyle.strokeWidth)

        return image
