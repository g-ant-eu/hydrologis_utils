from shapely.geometry import Polygon, Point, box
from PIL import Image, ImageDraw
from shapely.geometry.base import BaseGeometry
from shapely.affinity import affine_transform
from hydrologis_utils.geom_utils import HyGeomUtils, ExtendedGeometry
from hydrologis_utils.color_utils import HyColor
import math
from typing import List, Tuple
import requests
from io import BytesIO

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
    def tile2lon( x:int, zoom:int ) -> float:
        """ Convert a tile x coordinate to longitude.
        Note that the returned longitude represents the left side of the tile.
        :param x: the tile x coordinate
        :param zoom: the zoom level
        :return: the longitude in degrees
        """
        return x / pow(2.0, zoom) * 360.0 - 180.0
    
    @staticmethod
    def tile2lat( y:int, zoom:int ) -> float:
        """ Convert a tile y coordinate to latitude.

        Note that the returned latitute represents the top of the tile.

        :param y: the tile y coordinate
        :param zoom: the zoom level
        :return: the latitude in degrees
        """ 
        n = math.pi - (2.0 * math.pi * y) / pow(2.0, zoom)
        return math.degrees(math.atan(math.sinh(n)))
    
    @staticmethod
    def getTileXY( lon:float, lat:float, zoom:int ) -> Tuple[int, int]:
        """
        Get the tile x and y for a given longitude and latitude at a given zoom level.
        """
        lat_rad = math.radians(lat)
        n = pow(2.0, zoom)
        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - (math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi)) / 2.0 * n)
        return x, y

    @staticmethod
    def getTileBounds( x:int, y:int, zoom:int ) -> List[float]:
        """ Get the bounds of a tile in longitude and latitude.
        :param x: the tile x coordinate
        :param y: the tile y coordinate
        :param zoom: the zoom level
        :return: a list of [xmin, ymin, xmax, ymax] in longitude and latitude
        """
        xmin = HySlippyTiles.tile2lon(x, zoom)
        xmax = HySlippyTiles.tile2lon(x + 1, zoom)
        ymin = HySlippyTiles.tile2lat(y + 1, zoom)
        ymax = HySlippyTiles.tile2lat(y, zoom)
        return [xmin, ymin, xmax, ymax]
    
    @staticmethod
    def getImageFromTileService( tileService:str, envelopeLL:List[float], zoom:int, imageSize:Tuple[int, int], dumpPath:str = None ) -> Image:
        """
        Get an image from a tile service in a given envelope at a certain zoomlevel.

        :param tileService: the tile service URL, e.g. "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        :param envelopeLL: the envelope in longitude and latitude as a list of [xmin, ymin, xmax, ymax]
        :param zoom: the zoom level
        :param imageSize: the size of the image to return as a tuple (width, height)
        :param dumpPath: optional path to save the fetched tiles (for debugging purposes)
        :return: an Image object with the tile image
        """

        headers = {
            "User-Agent": "HydroloGISOpenMapUtils/1.0 (+https://github.com/g-ant-eu/hydrologis_utils; )",
            "Referer": "https://github.com/g-ant-eu/hydrologis_utils"  # if applicable
        }
        # Calculate the tile x and y coordinates for the envelope
        x1, y1 = HySlippyTiles.getTileXY(envelopeLL[0], envelopeLL[3], zoom)
        x2, y2 = HySlippyTiles.getTileXY(envelopeLL[2], envelopeLL[1], zoom)

        # Create a list of tile URLs to fetch
        tileUrls = []
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                tileUrl = tileService.format(z=zoom, x=x, y=y)
                tileUrls.append(tileUrl)


        # Fetch the tiles
        images = []
        for tileUrl in tileUrls:
            try:

                response = requests.get(tileUrl, headers=headers)
                response.raise_for_status()  # Ensure we got the image successfully

                tileImage = Image.open(BytesIO(response.content))
                images.append(tileImage)
            except Exception as e:
                print(f"Error fetching tile {tileUrl}: {e}")

        if not images:
            return None
        
        # Create a blank image to paste the tiles into
        tileWidth, tileHeight = images[0].size
        # Calculate the size of the full image
        tilesX = (x2 - x1 + 1)
        fullWidth = tilesX * tileWidth
        tilesY = (y2 - y1 + 1)
        fullHeight = tilesY * tileHeight
        tmpImageSize = (fullWidth, fullHeight)
        fullImage = Image.new("RGBA", tmpImageSize, (0, 0, 0, 0))
        for i, img in enumerate(images):
            # With x outer, y inner:
            # i = (x - x1)*tilesY + (y - y1)
            x = (i // tilesY) * tileWidth
            y = (i %  tilesY) * tileHeight
            fullImage.paste(img, (x, y))

            
        # Resize the full image to the requested size, but 
        # maintain the aspect ratio, in case override one dimension of imageSize
        if imageSize[0] != fullWidth or imageSize[1] != fullHeight:
            # calculate image ratio
            ratio = min(imageSize[0] / fullWidth, imageSize[1] / fullHeight)
            newSize = (int(fullWidth * ratio), int(fullHeight * ratio))
            fullImage = fullImage.resize(newSize, Image.Resampling.LANCZOS)
        
        if dumpPath:
            fullImage.save(dumpPath, format='PNG')

        return fullImage
        
        
    

class HyGeomRenderer():
    """
    Small utility to draw lat long geometries on an image.

    Usefull to create simple tiles.
    """
    def __init__(self, imageSize:Tuple[int, int]):
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

    def renderImage(self, imagesBoundsLongLat:List[float], geometriesLongLat:List, colorTable:dict=None , antialias:bool=False, intersectionBufferX:float=0, intersectionBufferY:float=0 ) -> Image:
        """
        Render the geometries on an image.

        :param imagesBoundsLongLat: the bounds of the image in long lat as a list of [xmin, ymin, xmax, ymax]
        :param geometriesLongLat: the geometries to render in long lat (this can be an ExtendedGeometry, in case theming with colorTable is used)
        :param colorTable: a dictionary of attribute values and styles to use for theming (the attribute comes from the ExtendedGeometry)
        :param antialias: if True, the image will be rendered with antialiasing (this is a workaround at the moment, rendering is made at double size and then resized)
        :param intersectionBufferX: a buffer to use to enlarge the tile bounds in x direction (useful when rendering points, that need to have partials included from the side tile)
        :param intersectionBufferY: a buffer to use to enlarge the tile bounds in y direction (useful when rendering points, that need to have partials included from the side tile)
        """
        # Create a bounding box geometry to check which geoms to include in the image rendering
        tile_box = box(imagesBoundsLongLat[0] - intersectionBufferX, imagesBoundsLongLat[1] - intersectionBufferY, imagesBoundsLongLat[2] + intersectionBufferX, imagesBoundsLongLat[3] + intersectionBufferY)

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

                style = None
                # check if the geometry has an attribute to use with the colortable
                if colorTable and attribute and attribute in colorTable:
                    style = colorTable[attribute]

                if scaledGeom.geom_type == "Polygon":
                    if not style:
                        style = self.polygonStyle
                    draw.polygon(scaledGeom.exterior.coords, outline=style.strokeColor.getRgba(), fill=style.fillColor.getRgba(), width=style.strokeWidth*factor)
                    for hole in scaledGeom.interiors:
                        draw.polygon(hole.coords, outline=style.strokeColor.getRgba(), fill=(0, 0, 0, 0), width=style.strokeWidth*factor)
                elif scaledGeom.geom_type == "MultiPolygon":
                    if not style:
                        style = self.polygonStyle
                    for poly in scaledGeom.geoms:
                        draw.polygon(poly.exterior.coords, outline=style.strokeColor.getRgba(), fill=style.fillColor.getRgba(), width=style.strokeWidth*factor)
                        for hole in poly.interiors:
                            draw.polygon(hole.coords, outline=style.strokeColor.getRgba(), fill=(0, 0, 0, 0), width=style.strokeWidth*factor)
                elif scaledGeom.geom_type == "LineString":
                    if not style:
                        style = self.lineStyle
                    draw.line(scaledGeom.coords, fill=style.strokeColor.getRgba(), width=style.strokeWidth*factor, joint="curve")
                elif scaledGeom.geom_type == "MultiLineString":
                    if not style:
                        style = self.lineStyle
                    for line in scaledGeom.geoms:
                        draw.line(line.coords, fill=style.strokeColor.getRgba(), width=style.strokeWidth*factor, joint="curve")
                elif scaledGeom.geom_type == "Point":
                    if not style:
                        style = self.pointStyle
                    halfSize = style.size/2
                    draw.ellipse([scaledGeom.x-halfSize, scaledGeom.y-halfSize, scaledGeom.x+halfSize, scaledGeom.y+halfSize], fill=style.fillColor.getRgba(), outline=style.strokeColor.getRgba(), width=style.strokeWidth*factor)
                elif scaledGeom.geom_type == "MultiPoint":
                    if not style:
                        style = self.pointStyle
                    halfSize = style.size/2
                    for point in scaledGeom.geoms:
                        draw.ellipse([point.x-halfSize, point.y-halfSize, point.x+halfSize, point.y+halfSize], fill=style.fillColor.getRgba(), outline=style.strokeColor.getRgba(), width=style.strokeWidth*factor)
                        
        del draw
        if antialias:
            image = image.resize(self.imageSize, Image.Resampling.LANCZOS)

        return image
    
    def transparentImage(self) -> Image:
        return Image.new("RGBA", self.imageSize, (0, 0, 0, 0))
