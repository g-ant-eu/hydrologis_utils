from shapely.wkt import loads, dumps
from shapely.wkb import loads as wkb_loads
from shapely.ops import split,snap, transform, linemerge
import numpy as np
# import shapely geometry
from shapely.geometry import GeometryCollection, LineString, MultiLineString, MultiPoint, MultiPolygon, Point, Polygon
import shapely
from shapely.geometry.base import BaseGeometry
import numpy as np

class ExtendedGeometry():
    """
    A class that extends the shapely BaseGeometry class.
    """
    def __init__(self, geom:BaseGeometry, attribute:any=None):
        self.geom = geom
        self.attribute = attribute

    def get_basegeometry(self) -> BaseGeometry:
        """
        Get the base geometry of the object.
        """
        return self.geom
    
    def get_srid(self) -> int:
        """
        Get the SRID of the geometry.
        """
        return shapely.get_srid(self.geom)
    
    def set_srid(self, srid:int) -> None:
        """
        Set the SRID of the geometry.
        """
        self.geom = shapely.set_srid(self.geom, srid)

    def rotate(self, angle:float, origin:Point) -> 'ExtendedGeometry':
        """
        Rotate the geometry by a given angle around a given origin.
        """
        geom = shapely.affinity.rotate(self.geom, angle, origin)
        return ExtendedGeometry(geom)

    def buffer(self, distance:float) -> 'ExtendedGeometry':
        """
        Buffer the geometry by a given distance.
        """
        return ExtendedGeometry(self.geom.buffer(distance))
    
    def get_coordinates(self) -> list:
        """
        Get the coordinates of the geometry.
        """
        return list(self.geom.coords)
    
    def get_area(self) -> float:
        """
        Get the area of the geometry.
        """
        return self.geom.area
    
    def get_length(self) -> float:
        """
        Get the length of the geometry.
        """
        return self.geom.length
    
    def get_bounds(self) -> tuple:
        """
        Get the bounds of the geometry.
        """
        return self.geom.bounds
    
    def get_centroid(self) -> Point:
        """
        Get the centroid of the geometry.
        """
        return self.geom.centroid
    
    def get_envelope(self) -> Polygon:
        """
        Get the envelope of the geometry.
        """
        return self.geom.envelope
    
    def get_intersection(self, other:'ExtendedGeometry') -> 'ExtendedGeometry':
        """
        Get the intersection of the geometry with another geometry.
        """
        return ExtendedGeometry(self.geom.intersection(other))
    
    def wkt(self) -> str:
        """
        Get the WKT representation of the geometry.
        """
        return HyGeomUtils.toWkt(self.geom)
    
    
class HyGeomUtils():

    @staticmethod
    def makeLineString(coordinates, srid:int=None, extended:bool=False) -> any:
        """
        Create a LineString from a list of coordinates.

        :param coordinates: the list of coordinates.
        :param srid: the SRID of the geometry.
        """
        if not isinstance(coordinates, list):
            raise Exception("The input coordinates must be a list.")
        line = LineString(coordinates)
        if srid:
            line = shapely.set_srid(line, srid)
        if extended:
            line = ExtendedGeometry(line)
        return line
    
    @staticmethod
    def makePolygon(coordinates, srid:int=None, extended:bool=False) -> any:
        """
        Create a Polygon from a list of coordinates.

        :param coordinates: the list of coordinates.
        :param srid: the SRID of the geometry.
        """
        if not isinstance(coordinates, list):
            raise Exception("The input coordinates must be a list.")
        polygon = Polygon(coordinates)
        if srid:
            polygon = shapely.set_srid(polygon, srid)
        if extended:
            polygon = ExtendedGeometry(polygon)
        return polygon
    
    @staticmethod
    def makePoint(coordinates, srid:int=None, extended:bool=False) -> any:
        """
        Create a Point from a list of coordinates.

        :param coordinates: the list of coordinates.
        :param srid: the SRID of the geometry.
        """
        if not isinstance(coordinates, list):
            raise Exception("The input coordinates must be a list.")
        point = Point(coordinates)
        if srid:
            point = shapely.set_srid(point, srid)
        if extended:
            point = ExtendedGeometry(point)
        return point

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
    def fromWkt(wkt:str, srid:int=None, extended:bool=False) -> any:
        if wkt[:4].upper().startswith("SRID"):
            # split to get srid and geom
            srid, geom = wkt.split(";")
            geom = loads(geom)
            srid = int(srid.split("=")[1])
            geom = shapely.set_srid(geom, srid)
        elif srid:
            geom = loads(wkt)
            geom = shapely.set_srid(geom, srid)
        else:
            geom = loads(wkt)
        if extended:
            geom = ExtendedGeometry(geom)
        return geom
    
    @staticmethod
    def toWkt(geom:BaseGeometry) -> str:
        srid = shapely.get_srid(geom)
        geom = dumps(geom)
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

        :param world: the world coordinate system as a list of [xmin, ymin, xmax, ymax]
        :param rect: the rectangle coordinate system as a list of [xmin, ymin, xmax, ymax]
        """
        rectWidth = (rect[2] - rect[0])
        rectHeight = (rect[3] - rect[1])
        worldWidth = (world[2] - world[0])
        worldHeight = (world[3] - world[1])

        translateMatrix = np.array([[1.0, 0.0, -world[0]],
              [0, 1, -world[1]],
              [0,  0,  1]])
        scaleMatrix = np.array([[rectWidth / worldWidth, 0, 0],
                [0, rectHeight / worldHeight, 0],
                [0,  0,  1]])
        mirrorMatrix = np.array([[1, 0, 0],
                [0, -1, rectHeight],
                [0, 0, 1]])
        translateScaleMatrix = np.dot(scaleMatrix, translateMatrix)
        transformMatrix = np.dot(mirrorMatrix, translateScaleMatrix)


        a = transformMatrix[0][0]
        b = transformMatrix[0][1]
        d = transformMatrix[1][0]
        e = transformMatrix[1][1]
        xoff = transformMatrix[0][2]
        yoff = transformMatrix[1][2]

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
    
