from shapely.geometry.base import BaseGeometry
from shapely.geometry import Point as ShapelyPoint
from shapely.geometry import LineString as ShapelyLineString
from shapely.geometry import Polygon as ShapelyPolygon
# from shapely.ops import transform
from geojson import Feature, FeatureCollection, Point, LineString, Polygon
import geojson
#, Point, 
#, loads, dumps

class HyGeojsonUtils():

    @staticmethod
    def mapToFeature( properties:dict, geometry:BaseGeometry, id:int=None ) -> Feature:
        """
        Create a geojson feature from a dictionary of properties and a geometry.

        This covers single geometries and polygons without holes.
        """
        if id is None:
            # try to get the id from the properties
            id = properties.get("id")
        if id is None:
            raise Exception("No id found in properties and no id given.")
        
        if isinstance(geometry, ShapelyPoint):
            geom = Point((geometry.x, geometry.y))
        elif isinstance(geometry, ShapelyLineString):
            geom = LineString(geometry.coords)
        elif isinstance(geometry, ShapelyPolygon):
            geom = Polygon(geometry.exterior.coords)
        else:
            raise Exception("Geometry type not supported.")
        feature = Feature(id=id, properties=properties, geometry=geom)
        return feature
    
    @staticmethod
    def stringToFeature( geojsonString:str ) -> Feature:
        """
        Create a geojson feature from a geojson string.
        """
        # decode the string
        feature = geojson.loads(geojsonString)
        return feature
    
    @staticmethod
    def stringToFeatureCollection( geojsonString:str ) -> FeatureCollection:
        """
        Create a geojson featurecollection from a geojson string.
        """
        # decode the string
        featureCollection = geojson.loads(geojsonString)
        return featureCollection

    @staticmethod
    def toFeatureCollection( features:list ) -> FeatureCollection:
        return FeatureCollection(features)

    @staticmethod
    def featureToString( feature:Feature ) -> str:
        """
        Create a geojson string from a geojson feature.
        """
        # encode the feature
        jsonString = geojson.dumps(feature)
        return jsonString
    
    @staticmethod
    def featureCollectionToString( featureCollection:FeatureCollection ) -> str:
        """
        Create a geojson string from a geojson featurecollection.
        """
        # encode the feature
        jsonString = geojson.dumps(featureCollection, sort_keys=True)
        return jsonString
    


