import math
import os
from io import BytesIO
from math import ceil, floor
from typing import List, Optional, Tuple

import requests
from PIL import Image, ImageDraw
from requests.adapters import HTTPAdapter, Retry
from shapely.affinity import affine_transform
from shapely.geometry import Point, Polygon, box
from shapely.geometry.base import BaseGeometry

from hydrologis_utils.color_utils import HyColor
from hydrologis_utils.geom_utils import ExtendedGeometry, HyGeomUtils


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
    def getTileXY(lon: float, lat: float, zoom: int, fractional: bool = False) -> Tuple[float, float]:
        """
        Get the tile x and y for a given longitude and latitude at a given zoom level.

        :param lon: Longitude in degrees
        :param lat: Latitude in degrees
        :param zoom: Zoom level
        :param fractional: If True, return fractional tile coordinates (floats).
                        If False, return integer tile coordinates (tile indices).
        :return: (x, y) tile coordinates
        """
        lat_rad = math.radians(lat)
        n = pow(2.0, zoom)
        x = (lon + 180.0) / 360.0 * n
        y = (1.0 - (math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi)) / 2.0 * n
        if fractional:
            return x, y
        else:
            return int(x), int(y)

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
    def getImageFromTileService(
        tileService: str,
        envelopeLL: List[float],  # [xmin, ymin, xmax, ymax] in lon/lat
        zoom: int,
        imageSize: Tuple[int, int],
        dumpPath: Optional[str] = None,
        timeout_s: float = 10.0,
    ) -> Optional[Image.Image]:

        # ---- Sanity checks
        if zoom < 0:
            zoom = 0
        max_x = (1 << zoom) - 1

        # Antimeridian handling: if xmin > xmax, assume envelope crosses 180°
        xmin, ymin, xmax, ymax = envelopeLL
        crosses_anti = xmin > xmax

        headers = {
            "User-Agent": "HydroloGISOpenMapUtils/1.0 (+https://github.com/g-ant-eu/hydrologis_utils)",
            "Referer": "https://github.com/g-ant-eu/hydrologis_utils"
        }

        # Robust session with retries (handles 429/5xx and some connection resets)
        sess = requests.Session()
        retries = Retry(
            total=5,
            connect=5,
            read=5,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET"])
        )
        sess.mount("https://", HTTPAdapter(max_retries=retries))
        sess.mount("http://", HTTPAdapter(max_retries=retries))

        def clamp_wrap_x(x):
            # wrap x modulo 2^z
            return x & max_x

        # Compute tile ranges; handle antimeridian by doing two ranges if needed
        def tile_range(xmin, ymin, xmax, ymax):
            x1, y1 = HySlippyTiles.getTileXY(xmin, ymax, zoom)
            x2, y2 = HySlippyTiles.getTileXY(xmax, ymin, zoom)
            # ensure ascending y
            if y1 > y2:
                y1, y2 = y2, y1
            return x1, y1, x2, y2

        ranges = []
        if crosses_anti:
            # left: xmin..180
            ranges.append(tile_range(xmin, ymin, 180.0, ymax))
            # right: -180..xmax
            ranges.append(tile_range(-180.0, ymin, xmax, ymax))
        else:
            ranges.append(tile_range(xmin, ymin, xmax, ymax))

        tileUrls = []
        for (x1, y1, x2, y2) in ranges:
            # ensure ascending x; we’ll wrap modulo if needed
            if (x2 - x1) < 0:
                x1, x2 = x2, x1
            for x in range(x1, x2 + 1):
                for y in range(y1, y2 + 1):
                    xx = clamp_wrap_x(x)
                    tileUrls.append(tileService.format(z=zoom, x=xx, y=y))

        if not tileUrls:
            # Nothing to fetch – coordinates likely wrong
            raise ValueError(f"No tile URLs generated for envelope {envelopeLL} at z={zoom}")

        images = []
        errors = []
        for url in tileUrls:
            try:
                r = sess.get(url, headers=headers, timeout=timeout_s)
                r.raise_for_status()
                img = Image.open(BytesIO(r.content))
                img.load()  # force decode now to surface errors
                images.append(img.convert("RGBA"))
            except Exception as e:
                errors.append((url, str(e)))

        if not images:
            # Surface at least one concrete error to help debugging in Docker logs
            sample = errors[0] if errors else ("<no-url>", "Unknown error")
            raise RuntimeError(f"Failed to fetch any tiles. First error: {sample[0]} -> {sample[1]}")

        # Stitch (assumes images were fetched in x-major, y-minor order from ranges)
        tileWidth, tileHeight = images[0].size

        # Recompute full grid size
        # (Build a map from (x,y)->img so we can paste by coordinates robustly)
        # Recreate the (x,y) sequences we used to build tileUrls:
        xy_list = []
        for (x1, y1, x2, y2) in ranges:
            if (x2 - x1) < 0:
                x1, x2 = x2, x1
            for x in range(x1, x2 + 1):
                for y in range(y1, y2 + 1):
                    xy_list.append((clamp_wrap_x(x), y))

        # Normalize origins to the min x,y in the stitched mosaic space
        xs = [x for x, _ in xy_list]
        ys = [y for _, y in xy_list]
        min_x, min_y = min(xs), min(ys)
        max_x_grid, max_y_grid = max(xs), max(ys)

        fullWidth = (max_x_grid - min_x + 1) * tileWidth
        fullHeight = (max_y_grid - min_y + 1) * tileHeight
        fullImage = Image.new("RGBA", (fullWidth, fullHeight), (0, 0, 0, 0))

        for (img, (x, y)) in zip(images, xy_list):
            px = (x - min_x) * tileWidth
            py = (y - min_y) * tileHeight
            fullImage.paste(img, (px, py))

        # Crop to exact envelope using fractional tile coords
        xUL, yUL = HySlippyTiles.getTileXY(xmin, ymax, zoom, fractional=True)
        xLR, yLR = HySlippyTiles.getTileXY(xmax, ymin, zoom, fractional=True)

        # Remap to mosaic origin (min_x, min_y)
        crop_left   = (xUL - min_x) * tileWidth
        crop_top    = (yUL - min_y) * tileHeight
        crop_right  = (xLR - min_x) * tileWidth
        crop_bottom = (yLR - min_y) * tileHeight

        left   = max(0, int(floor(min(crop_left,  crop_right))))
        right  = min(fullWidth,  int(ceil(max(crop_left,  crop_right))))
        top    = max(0, int(floor(min(crop_top,   crop_bottom))))
        bottom = min(fullHeight, int(ceil(max(crop_top,   crop_bottom))))

        if right > left and bottom > top:
            fullImage = fullImage.crop((left, top, right, bottom))

        # Resize with aspect preserved
        cw, ch = fullImage.size
        if imageSize != (cw, ch):
            ratio = min(imageSize[0] / cw, imageSize[1] / ch)
            newSize = (max(1, int(round(cw * ratio))), max(1, int(round(ch * ratio))))
            fullImage = fullImage.resize(newSize, Image.Resampling.LANCZOS)

        if dumpPath:
            # ensure parent exists and is writable
            os.makedirs(os.path.dirname(dumpPath) or ".", exist_ok=True)
            fullImage.save(dumpPath, format="PNG")

        return fullImage


    # @staticmethod
    # def getImageFromTileService( 
    #     tileService:str, 
    #     envelopeLL:List[float], 
    #     zoom:int, 
    #     imageSize:Tuple[int, int], 
    #     dumpPath:Optional[str] = None ) -> Image:
    #     """
    #     Get an image from a tile service in a given envelope at a certain zoomlevel.

    #     :param tileService: the tile service URL, e.g. "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    #     :param envelopeLL: the envelope in longitude and latitude as a list of [xmin, ymin, xmax, ymax]
    #     :param zoom: the zoom level
    #     :param imageSize: the size of the image to return as a tuple (width, height)
    #     :param dumpPath: optional path to save the fetched tiles (for debugging purposes)
    #     :return: an Image object with the tile image
    #     """

    #     headers = {
    #         "User-Agent": "HydroloGISOpenMapUtils/1.0 (+https://github.com/g-ant-eu/hydrologis_utils; )",
    #         "Referer": "https://github.com/g-ant-eu/hydrologis_utils"  # if applicable
    #     }
    #     # Calculate the tile x and y coordinates for the envelope
    #     x1, y1 = HySlippyTiles.getTileXY(envelopeLL[0], envelopeLL[3], zoom)
    #     x2, y2 = HySlippyTiles.getTileXY(envelopeLL[2], envelopeLL[1], zoom)

    #     # Create a list of tile URLs to fetch
    #     tileUrls = []
    #     for x in range(x1, x2 + 1):
    #         for y in range(y1, y2 + 1):
    #             tileUrl = tileService.format(z=zoom, x=x, y=y)
    #             tileUrls.append(tileUrl)


    #     # Fetch the tiles
    #     images = []
    #     for tileUrl in tileUrls:
    #         try:

    #             response = requests.get(tileUrl, headers=headers)
    #             response.raise_for_status()  # Ensure we got the image successfully

    #             tileImage = Image.open(BytesIO(response.content))
    #             images.append(tileImage)
    #         except Exception as e:
    #             print(f"Error fetching tile {tileUrl}: {e}")

    #     if not images:
    #         return None
        
    #     # Create a blank image to paste the tiles into
    #     tileWidth, tileHeight = images[0].size
    #     # Calculate the size of the full image
    #     tilesX = (x2 - x1 + 1)
    #     fullWidth = tilesX * tileWidth
    #     tilesY = (y2 - y1 + 1)
    #     fullHeight = tilesY * tileHeight
    #     tmpImageSize = (fullWidth, fullHeight)
    #     fullImage = Image.new("RGBA", tmpImageSize, (0, 0, 0, 0))
    #     for i, img in enumerate(images):
    #         # With x outer, y inner:
    #         # i = (x - x1)*tilesY + (y - y1)
    #         x = (i // tilesY) * tileWidth
    #         y = (i %  tilesY) * tileHeight
    #         fullImage.paste(img, (x, y))


    #     # The image size is now expanded to adapt to contain tghe complete tiles. 
    #     # We now need to crop away the parts that are outside the envelope.

    #     # Fractional tile coords for the envelope corners
    #     xUL, yUL = HySlippyTiles.getTileXY(envelopeLL[0], envelopeLL[3], zoom, fractional=True)
    #     xLR, yLR = HySlippyTiles.getTileXY(envelopeLL[2], envelopeLL[1], zoom, fractional=True)

    #     # Convert to pixel offsets within stitched image whose origin is at (x1, y1)
    #     crop_left = (xUL - x1) * tileWidth
    #     crop_top = (yUL - y1) * tileHeight
    #     crop_right = (xLR - x1) * tileWidth
    #     crop_bottom = (yLR - y1) * tileHeight

    #     # Use floor for left/top and ceil for right/bottom to fully include the envelope,
    #     # then clamp to image bounds.
    #     from math import ceil, floor
    #     left = max(0, int(floor(crop_left)))
    #     top = max(0, int(floor(crop_top)))
    #     right = min(fullWidth,  int(ceil(crop_right)))
    #     bottom = min(fullHeight, int(ceil(crop_bottom)))

    #     if right > left and bottom > top:
    #         fullImage = fullImage.crop((left, top, right, bottom))
    #         croppedWidth, croppedHeight = fullImage.size
    #     else:
    #         # Fallback: nothing to crop (shouldn't happen if inputs are valid)
    #         croppedWidth, croppedHeight = fullWidth, fullHeight
    #     # -----------------------------------------------
            
    #     # Resize the full image to the requested size, but 
    #     # maintain the aspect ratio, in case override one dimension of imageSize
    #     if imageSize[0] != croppedWidth or imageSize[1] != croppedHeight:
    #         ratio = min(imageSize[0] / croppedWidth, imageSize[1] / croppedHeight)
    #         newSize = (int(round(croppedWidth * ratio)), int(round(croppedHeight * ratio)))
    #         fullImage = fullImage.resize(newSize, Image.Resampling.LANCZOS)

        
    #     if dumpPath:
    #         fullImage.save(dumpPath, format='PNG')

    #     return fullImage
        
        
    

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
