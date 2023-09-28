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
    def splitLineEquidistant(line:LineString, distanceDelta:float = 3.0) -> list:
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
        return loads(wkt)
    
    @staticmethod
    def toWkt(geom:BaseGeometry) -> str:
        return dumps(geom)
    
    @staticmethod
    def toWkb(geom:BaseGeometry) -> bytes:
        return geom.wkb
    
    @staticmethod
    def fromWkb(wkb:bytes) -> BaseGeometry:
        return wkb_loads(wkb)
    
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