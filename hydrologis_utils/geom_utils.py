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
    def splitLineEquidistant(line:LineString, segmentLength:float = 3.0) -> list:
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
    def splitLineEquidistantShply(line:LineString, distanceDelta:float = 3.0) -> list:
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