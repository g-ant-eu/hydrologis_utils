from hydrologis_utils.geojson_utils import HyGeojsonUtils
from hydrologis_utils.geom_utils import HyGeomUtils
import geojson
import unittest

# run with python3 -m unittest discover tests/

pointsCollection = """
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "id": 1,
      "properties": {
        "title": "feature 1"
      },
      "geometry": {
        "coordinates": [
          10.987663413499519,
          45.43936128790165
        ],
        "type": "Point"
      }
    },
    {
      "type": "Feature",
      "id": 2,
      "properties": {
        "title": "feature 2"
      },
      "geometry": {
        "coordinates": [
          11.12369907898011,
          46.079979520641416
        ],
        "type": "Point"
      }
    },
    {
      "type": "Feature",
      "id": 3,
      "properties": {
        "title": "feature 3"
      },
      "geometry": {
        "coordinates": [
          11.35495971029664,
          46.49829122651889
        ],
        "type": "Point"
      }
    }
  ]
}
"""

pointFeature = """
{
    "type": "Feature",
    "id": 1,
    "properties": {
        "title": "feature 1"
    },
    "geometry": {
        "coordinates": [
            10.987663413499519,
            45.43936128790165
        ],
        "type": "Point"
    }
}
"""

lineFeature = """
{
  "id": 1,
  "type": "Feature",
  "properties": {
    "title": "feature 1"
  },
  "geometry": {
    "coordinates": [
      [
        11.355362978411165,
        46.4872808118985
      ],
      [
        11.099520241670547,
        46.08495435499242
      ],
      [
        10.96454808921655,
        45.44271657526238
      ]
    ],
    "type": "LineString"
  }
}
"""

lineCollection = """
{
  "type": "FeatureCollection",
  "features": [
      {
        "id": 1,
        "type": "Feature",
        "properties": {
          "title": "feature 1"
        },
        "geometry": {
          "coordinates": [
            [
              11.355362978411165,
              46.4872808118985
            ],
            [
              11.099520241670547,
              46.08495435499242
            ],
            [
              10.96454808921655,
              45.44271657526238
            ]
          ],
          "type": "LineString"
        }
      }
  ]
}
"""


polygonCollection = """
{
  "type": "FeatureCollection",
  "features": [
    {
      "id": 1,
      "type": "Feature",
      "properties": {
        "title": "Garda Lake"
      },
      "geometry": {
        "coordinates": [
          [
            [
              10.841662995192195,
              45.88338400154231
            ],
            [
              10.523370456569722,
              45.61066335859627
            ],
            [
              10.50322535918832,
              45.482278576812206
            ],
            [
              10.694603804313573,
              45.42716678821057
            ],
            [
              10.74740715336921,
              45.48815209230696
            ],
            [
              10.7051024488687,
              45.59961216326994
            ],
            [
              10.900509893466023,
              45.86397030373837
            ],
            [
              10.841662995192195,
              45.88338400154231
            ]
          ]
        ],
        "type": "Polygon"
      }
    },
    {
      "type": "Feature",
      "id": 2,
      "properties": {
        "title": "Idro Lake"
      },
      "geometry": {
        "coordinates": [
          [
            [
              10.50566598479594,
              45.81344539313932
            ],
            [
              10.453288731604317,
              45.729135253906776
            ],
            [
              10.55199970877186,
              45.797998075056
            ],
            [
              10.50566598479594,
              45.81344539313932
            ]
          ]
        ],
        "type": "Polygon"
      }
    }
  ]
}
"""

polygonFeature = """
{
  "type": "Feature",
  "id": 2,
  "properties": {
    "title": "Idro Lake"
  },
  "geometry": {
    "coordinates": [
      [
        [
          10.50566598479594,
          45.81344539313932
        ],
        [
          10.453288731604317,
          45.729135253906776
        ],
        [
          10.55199970877186,
          45.797998075056
        ],
        [
          10.50566598479594,
          45.81344539313932
        ]
      ]
    ],
    "type": "Polygon"
  }
}
"""

class TestGeojson(unittest.TestCase):
    
    def test_feature_point(self):
        feature = HyGeojsonUtils.stringToFeature(pointFeature)
        self.assertTrue(isinstance(feature, geojson.Feature))
        self.assertEqual(feature.id, 1)
        self.assertEqual(feature.properties["title"], "feature 1")
        self.assertEqual(feature.geometry.type, "Point")
        self.assertEqual(len(feature.geometry.coordinates), 2)
        
    def test_featurecollection_point(self):
        featureCollection = HyGeojsonUtils.stringToFeatureCollection(pointsCollection)
        self.assertTrue(isinstance(featureCollection, geojson.FeatureCollection))
        self.assertEqual(len(featureCollection.features), 3)

        for feature in featureCollection.features:
            self.assertTrue(isinstance(feature, geojson.Feature))
            self.assertEqual(feature.id, 1)
            self.assertEqual(feature.properties["title"], "feature 1")
            self.assertEqual(feature.geometry.type, "Point")
            self.assertEqual(len(feature.geometry.coordinates), 2)
            break
    
    def test_feature_from_dictionary_point(self):
        point = HyGeomUtils.fromWkt("POINT (10.987663413499519 45.43936128790165)")
        feature = HyGeojsonUtils.mapToFeature({"id": 1, "title": "feature 1"}, point)
        self.assertTrue(isinstance(feature, geojson.Feature))
        self.assertEqual(feature.id, 1)
        self.assertEqual(feature.properties["title"], "feature 1")
        self.assertEqual(feature.geometry.type, "Point")
        self.assertEqual(len(feature.geometry.coordinates), 2)
    
    def test_feature_line(self):
        feature = HyGeojsonUtils.stringToFeature(lineFeature)
        self.assertTrue(isinstance(feature, geojson.Feature))
        self.assertEqual(feature.id, 1)
        self.assertEqual(feature.properties["title"], "feature 1")
        self.assertEqual(feature.geometry.type, "LineString")
        self.assertEqual(len(feature.geometry.coordinates), 3)
        
    def test_featurecollection_line(self):
        featureCollection = HyGeojsonUtils.stringToFeatureCollection(lineCollection)
        self.assertTrue(isinstance(featureCollection, geojson.FeatureCollection))
        self.assertEqual(len(featureCollection.features), 1)

        for feature in featureCollection.features:
            self.assertTrue(isinstance(feature, geojson.Feature))
            self.assertEqual(feature.id, 1)
            self.assertEqual(feature.properties["title"], "feature 1")
            self.assertEqual(feature.geometry.type, "LineString")
            self.assertEqual(len(feature.geometry.coordinates), 3)
            break
    
    def test_feature_from_dictionary_line(self):
        point = HyGeomUtils.fromWkt("LINESTRING (10.987663413499519 45.43936128790165, 11.12369907898011 46.079979520641416, 11.35495971029664 46.49829122651889)")
        feature = HyGeojsonUtils.mapToFeature({"id": 1, "title": "feature 1"}, point)
        self.assertTrue(isinstance(feature, geojson.Feature))
        self.assertEqual(feature.id, 1)
        self.assertEqual(feature.properties["title"], "feature 1")
        self.assertEqual(feature.geometry.type, "LineString")
        self.assertEqual(len(feature.geometry.coordinates), 3)
       
    def test_feature_polygon(self):
        feature = HyGeojsonUtils.stringToFeature(polygonFeature)
        self.assertTrue(isinstance(feature, geojson.Feature))
        self.assertEqual(feature.id, 2)
        self.assertEqual(feature.properties["title"], "Idro Lake")
        self.assertEqual(feature.geometry.type, "Polygon")
        self.assertEqual(len(feature.geometry.coordinates[0]), 4)
        
    def test_featurecollection_polygon(self):
        featureCollection = HyGeojsonUtils.stringToFeatureCollection(polygonCollection)
        self.assertTrue(isinstance(featureCollection, geojson.FeatureCollection))
        self.assertEqual(len(featureCollection.features), 2)

        for feature in featureCollection.features:
            self.assertTrue(isinstance(feature, geojson.Feature))
            self.assertEqual(feature.id, 1)
            self.assertEqual(feature.properties["title"], "Garda Lake")
            self.assertEqual(feature.geometry.type, "Polygon")
            self.assertEqual(len(feature.geometry.coordinates[0]), 8)
            break
    
    def test_feature_from_dictionary_polygon(self):
        point = HyGeomUtils.fromWkt("POLYGON ((10.50566598479594 45.81344539313932, 10.453288731604317 45.729135253906776, 10.55199970877186 45.797998075056, 10.50566598479594 45.81344539313932))")
        feature = HyGeojsonUtils.mapToFeature({"id": 1, "title": "feature 1"}, point)
        self.assertTrue(isinstance(feature, geojson.Feature))
        self.assertEqual(feature.id, 1)
        self.assertEqual(feature.properties["title"], "feature 1")
        self.assertEqual(feature.geometry.type, "Polygon")
        self.assertEqual(len(feature.geometry.coordinates), 4)
       
        




if __name__ == "__main__":
    unittest.main()