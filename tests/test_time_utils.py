from hydrologis_utils.time_utils import *

import unittest

# run with python3 -m unittest discover tests/

class TestStrings(unittest.TestCase):
    CHECKDATE = "2021-12-24 12:00:00"
    
    def test_new_datetime(self):
        string = self.CHECKDATE

        dt = new_datetime(string)

        str = to_string_with_seconds(dt)

        self.assertEqual(string, str)

    def test_new_datetime_utc(self):
        string = self.CHECKDATE

        dt = new_datetime_utc(string)

        str = to_string_with_seconds(dt)

        self.assertEqual(string, str)
    
    def test_quick_to_string(self):
        string = self.CHECKDATE
        dt = new_datetime(string)
        str = quick_to_string(dt.timestamp())

        self.assertEqual(string, str)
    
    def test_quick_utc_to_string(self):
        string = self.CHECKDATE
        dt = new_datetime_utc(string)
        str = quick_utc_to_string(dt.timestamp())

        self.assertEqual(string, str)         

if __name__ == "__main__":
    unittest.main()