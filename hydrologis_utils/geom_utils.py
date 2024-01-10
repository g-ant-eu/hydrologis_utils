from shapely.wkt import loads, dumps
from shapely.wkb import loads as wkb_loads
from shapely.ops import split,snap, transform, linemerge
import numpy as np
# import shapely geometry
from shapely.geometry import GeometryCollection, LineString, MultiLineString, MultiPoint, MultiPolygon, Point, Polygon
import shapely
from shapely.geometry.base import BaseGeometry

class HyGeomUtils():

    # static method to convert geometry to 2D
    @staticmethod
    def convert2D( geom:BaseGeometry ) -> BaseGeometry:
        if geom.has_z:
            geom = transform(lambda x,y,z=None: (x,y), geom)
        return geom
    

    @staticmethod
    def splitLineEquidistant(line:LineString, segmentLength:float = 3.0) -> list[LineString]:
        if not isinstance(line, LineString):
            raise Exception("The input geometry must be a LineString.")
        lineCoords = list(line.coords)
        
        lastSegment = [] # Coordinates
        segments = [] # LineString segments
        accumulatedLength = 0.0

        i = 0
        while i < len(lineCoords)-1:
            c1 = lineCoords[i]
            c2 = lineCoords[i+1]

            lastSegment.append(c1)

            length = Point(c1).distance(Point(c2))
            if length + accumulatedLength >= segmentLength:
                offsetLength = segmentLength - accumulatedLength
                ratio = offsetLength / length
                dx = c2[0] - c1[0]
                dy = c2[1] - c1[1]

                segmentationPoint = (c1[0] + (dx * ratio), c1[1] + (dy * ratio))
                lastSegment.append(segmentationPoint)
                segments.append(LineString(lastSegment))

                lastSegment = []
                accumulatedLength = 0.0
                if not segmentationPoint in lineCoords:
                    lineCoords.insert(i+1, segmentationPoint)
            else:
                accumulatedLength += length

            i += 1

        lastSegment.append(lineCoords[-1])
        segments.append(LineString(lastSegment))
        return segments
            

        
    @staticmethod
    def splitLineEquidistantShply(line:LineString, distanceDelta:float = 3.0) -> list[LineString]:
        if not isinstance(line, LineString):
            raise Exception("The input geometry must be a LineString.")
        # generate the equidistant points
        distances = np.arange(0, line.length, distanceDelta)
        interpPoints = [line.interpolate(distance) for distance in distances]
        # then add the last coordinate point
        lastCoord = list(line.coords)[-1]
        interpPoints.append(Point(lastCoord))
        points = MultiPoint(interpPoints)
        segmentsGc = split(snap(line, points, 1.0e-5), points)

        linesList = [line for line in segmentsGc.geoms]
        return linesList

    
    @staticmethod
    def fromWkt(wkt:str) -> BaseGeometry:
        if wkt[:4].upper().startswith("SRID"):
            # split to get srid and geom
            srid, geom = wkt.split(";")
            geom = loads(geom)
            srid = int(srid.split("=")[1])
            geom = shapely.set_srid(geom, srid)
            return geom
        else:
            return loads(wkt)
    
    @staticmethod
    def toWkt(geom:BaseGeometry) -> str:
        geom = dumps(geom)
        srid = shapely.get_srid(geom)
        if srid is not None:
            geom = "SRID={};{}".format(srid, geom)
        return geom
    
    @staticmethod
    def toWkb(geom:BaseGeometry) -> bytes:
        return geom.wkb
    
    @staticmethod
    def fromWkb(wkb:bytes) -> BaseGeometry:
        return wkb_loads(wkb)
    
    @staticmethod
    def toGeoJson(geom:BaseGeometry, indent:int=None) -> str:
        return shapely.to_geojson(geom, indent=indent)
    
    @staticmethod
    def fromGeoJson(geojson:str) -> BaseGeometry:
        return shapely.from_geojson(geojson)
    
    @staticmethod
    def joinLines(lines:any) -> any:
        if isinstance(lines, list):
            lines = MultiLineString(lines)
        elif isinstance(lines, GeometryCollection):
            lines = MultiLineString([line for line in lines.geoms])
        
        if isinstance(lines, MultiLineString) and len(lines.geoms) == 1:
            return lines.geoms[0]

        mergedLines = linemerge(lines)
        return mergedLines
    
    @staticmethod
    def toMultiLineString(geom:BaseGeometry) -> BaseGeometry:
        if isinstance(geom, LineString):
            geom = MultiLineString([geom])
        elif isinstance(geom, MultiLineString):
            geom = geom
        elif isinstance(geom, Polygon):
            # extract the exterior ring
            geom = MultiLineString([geom.exterior])
        elif isinstance(geom, MultiPolygon):
            # extract the exterior rings
            geom = MultiLineString([poly.exterior for poly in geom.geoms])
        else:
            raise Exception("The input geometry must be a LineString/MultiLineString or Polygon/Multipolygon.")
        return geom
    
    @staticmethod
    def worldToRectangleMatrix(world:[float], rect:[int]) -> list[float]:
        """
        Get the scaling transformation matrix to transform from a world coordinate system 
        to a rectangle coordinate system, following shapely's affine_transform.

        For 2D affine transformations, the 6 parameter matrix is::

            [a, b, d, e, xoff, yoff]

        which represents the augmented matrix::

            [x']   / a  b xoff \ [x]
            [y'] = | d  e yoff | [y]
            [1 ]   \ 0  0   1  / [1]
        """
        rectWidth = (rect[2] - rect[0])
        rectHeight = (rect[3] - rect[1])
        a = rectWidth / (world[2] - world[0])
        b = 0
        d = 0
        e = -1 * rectHeight / (world[3] - world[1])
        xoff = a * (-world[0])
        yoff = rectHeight - (-world[1])

        return [a, b, d, e, xoff, yoff]
    

class HySTRTreeIndex():
    """
    Wrapper for shapely STRtree index.
    """
    
    def __init__(self, geomList:list[BaseGeometry], referenceList:list = None):
        """
        Initialize the index.

        :param geomList: the list of geometries to index.
        :param referenceList: the list of reference objects to index. If this is set, then the
                        various query methods will return the reference objects instead of the 
                        geometries. Naturally it has to have the same dimension as the geomList.
        """
        self.geomList = geomList
        self.index = shapely.STRtree(geomList)
        self.referenceList = referenceList
        if referenceList is not None and len(referenceList) != len(geomList):
            raise Exception("The reference list must have the same dimension as the geometry list.")

    def query(self, geom:BaseGeometry) -> list[BaseGeometry]:
        """
        Query the spatial index for bounding box intersecting geometries.

        :param geom: the geometry to query for.

        :return: a list of intersecting geometries
        """
        indexes = self.index.query(geom)
        if self.referenceList:
            return [self.referenceList[i] for i in indexes]
        return [self.geomList[i] for i in indexes]
    
    def queryNearest(self, geom:BaseGeometry, maxDistance:float = None) -> BaseGeometry:
        """
        Query the spatial index for the nearest geometry to a given geometry.

        :param geom: the geometry to query for.
        :param maxDistance: the maximum distance to search for.

        :return: the nearest geometry or none.
        """
        nearestGeomIndex = self.index.query_nearest(geom, max_distance=maxDistance)
        if nearestGeomIndex is not None:
            index = None
            if isinstance(nearestGeomIndex, np.ndarray ) or isinstance(nearestGeomIndex, list):
                if len(nearestGeomIndex) == 0:
                    return None
                index = nearestGeomIndex[0]
            else:
                index = nearestGeomIndex
        
            if self.referenceList:
                return self.referenceList[index]
            return self.geomList[index]
        return None
    
