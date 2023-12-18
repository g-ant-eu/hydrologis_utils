
import pyproj
from shapely.ops import transform as shpTransform
from shapely.geometry.base import BaseGeometry

class HyProjManager():

    # constructor with source and destination epsg
    def __init__(self, sourceEpsgSrid:int, destinationEpsgSrid:int):
        self.sourceEpsg = sourceEpsgSrid
        self.destinationEpsg = destinationEpsgSrid
        self.sourceProj = pyproj.CRS(f'EPSG:{sourceEpsgSrid}')
        self.destProj = pyproj.CRS(f'EPSG:{destinationEpsgSrid}')

        self.transformation = pyproj.Transformer.from_crs(self.sourceEpsg, self.destinationEpsg, always_xy=True).transform


    def transform(self, geom:BaseGeometry) -> BaseGeometry:
        return shpTransform(self.transformation, geom)